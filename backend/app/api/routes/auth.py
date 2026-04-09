from __future__ import annotations

import logging
from hmac import compare_digest
from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import RateLimitError, SecurityError, UnauthorizedError
from app.core.request_security import ensure_allowed_origin, ensure_csrf, issue_csrf_token
from app.db.session import get_db
from app.schemas.auth import AuthResponse, LoginRequest, MessageResponse, RefreshRequest, RegisterRequest
from app.schemas.user import UserRead
from app.services.auth_service import AuthService, login_rate_limiter
from app.services.token_service import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger(__name__)


def _request_ip(request: Request) -> Optional[str]:
    if request.client is None:
        return None
    return request.client.host


def _set_auth_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _set_refresh_cookie(response: Response, refresh_token: str, csrf_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        path=settings.refresh_cookie_path,
        domain=settings.cookie_domain,
    )
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.csrf_cookie_samesite,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        path=settings.csrf_cookie_path,
        domain=settings.cookie_domain,
    )
    _set_auth_headers(response)


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        domain=settings.cookie_domain,
    )
    response.delete_cookie(
        key=settings.csrf_cookie_name,
        path=settings.csrf_cookie_path,
        domain=settings.cookie_domain,
    )
    _set_auth_headers(response)


def _auth_response(user, access_token: str, expires_in: int) -> AuthResponse:
    return AuthResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserRead.model_validate(user),
    )


def _resolve_refresh_token(request: Request, payload: Optional[RefreshRequest]) -> str:
    body_refresh_token = (payload or RefreshRequest()).refresh_token
    cookie_refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if body_refresh_token:
        if not settings.allow_refresh_token_in_body:
            raise SecurityError("리프레시 토큰 본문 전달은 허용되지 않습니다.")
        if cookie_refresh_token and not compare_digest(cookie_refresh_token, body_refresh_token):
            raise SecurityError("리프레시 토큰 전달 방식이 일치하지 않습니다.")
    refresh_token = cookie_refresh_token or body_refresh_token
    if not refresh_token:
        raise UnauthorizedError("리프레시 토큰이 없습니다.")
    return refresh_token


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    ensure_allowed_origin(request, settings)
    auth_service = AuthService(db)
    token_service = TokenService(db)
    user = auth_service.register_user(payload)
    tokens = token_service.issue_tokens(user, request.headers.get("user-agent"), _request_ip(request))
    _set_refresh_cookie(response, tokens.refresh_token, issue_csrf_token())
    return _auth_response(user, tokens.access_token, tokens.expires_in)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    ensure_allowed_origin(request, settings)
    normalized_email = payload.email.lower()
    request_ip = _request_ip(request)
    if not login_rate_limiter.is_allowed(
        db,
        normalized_email,
        request_ip,
        settings.login_rate_limit_attempts,
        settings.login_rate_limit_window_seconds,
    ):
        logger.warning("Login rate limit exceeded email=%s ip=%s", normalized_email, request_ip)
        raise RateLimitError()

    auth_service = AuthService(db)
    try:
        user = auth_service.authenticate_user(payload.email, payload.password)
    except UnauthorizedError:
        login_rate_limiter.record_failure(db, normalized_email, request_ip)
        raise

    login_rate_limiter.clear(db, normalized_email, request_ip)
    tokens = TokenService(db).issue_tokens(user, request.headers.get("user-agent"), request_ip)
    _set_refresh_cookie(response, tokens.refresh_token, issue_csrf_token())
    return _auth_response(user, tokens.access_token, tokens.expires_in)


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: Request,
    response: Response,
    payload: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db),
) -> AuthResponse:
    ensure_allowed_origin(request, settings)
    ensure_csrf(request, settings)
    refresh_token = _resolve_refresh_token(request, payload)
    user, tokens = TokenService(db).rotate_refresh_token(
        refresh_token,
        request.headers.get("user-agent"),
        _request_ip(request),
    )
    _set_refresh_cookie(response, tokens.refresh_token, issue_csrf_token())
    return _auth_response(user, tokens.access_token, tokens.expires_in)


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    payload: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db),
) -> MessageResponse:
    ensure_allowed_origin(request, settings)
    ensure_csrf(request, settings)
    refresh_token = None
    try:
        refresh_token = _resolve_refresh_token(request, payload)
    except UnauthorizedError:
        logger.info("Logout requested without a valid refresh token.")
    TokenService(db).revoke_refresh_token(refresh_token)
    _clear_refresh_cookie(response)
    return MessageResponse(message="로그아웃되었습니다.")


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)

from __future__ import annotations

import hmac
import secrets
from typing import Optional
from urllib.parse import urlparse

from fastapi import Request

from app.core.config import Settings
from app.core.exceptions import SecurityError


def issue_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def _extract_origin(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def get_request_origin(request: Request) -> Optional[str]:
    origin = request.headers.get("origin")
    if origin:
        return _extract_origin(origin)
    referer = request.headers.get("referer")
    return _extract_origin(referer)


def ensure_allowed_origin(request: Request, settings: Settings) -> None:
    origin = get_request_origin(request)
    if origin is None:
        if settings.is_production:
            raise SecurityError("Origin 또는 Referer 검증에 실패했습니다.")
        return
    if origin not in settings.csrf_trusted_origins:
        raise SecurityError("허용되지 않은 요청 출처입니다.")


def ensure_csrf(request: Request, settings: Settings) -> None:
    csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
    csrf_header = request.headers.get(settings.csrf_header_name)
    if not csrf_cookie or not csrf_header:
        raise SecurityError("CSRF 검증에 실패했습니다.")
    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise SecurityError("CSRF 검증에 실패했습니다.")

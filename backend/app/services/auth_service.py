from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.login_attempt import LoginAttempt
from app.models.user import User
from app.schemas.auth import RegisterRequest

logger = logging.getLogger(__name__)


class LoginRateLimiter:
    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _normalize_ip(ip_address: Optional[str]) -> str:
        return ip_address or "unknown"

    def prune(self, db: Session, window_seconds: int) -> None:
        window_start = self._now() - timedelta(seconds=window_seconds)
        db.execute(delete(LoginAttempt).where(LoginAttempt.attempted_at < window_start))
        db.commit()

    def is_allowed(
        self,
        db: Session,
        email: str,
        ip_address: Optional[str],
        max_attempts: int,
        window_seconds: int,
    ) -> bool:
        self.prune(db, window_seconds)
        window_start = self._now() - timedelta(seconds=window_seconds)
        normalized_ip = self._normalize_ip(ip_address)
        email_failures = db.scalar(
            select(func.count(LoginAttempt.id)).where(
                LoginAttempt.successful.is_(False),
                LoginAttempt.email == email,
                LoginAttempt.attempted_at >= window_start,
            )
        )
        ip_failures = db.scalar(
            select(func.count(LoginAttempt.id)).where(
                LoginAttempt.successful.is_(False),
                LoginAttempt.ip_address == normalized_ip,
                LoginAttempt.attempted_at >= window_start,
            )
        )
        return (email_failures or 0) < max_attempts and (ip_failures or 0) < max_attempts

    def record_failure(self, db: Session, email: str, ip_address: Optional[str]) -> None:
        db.add(
            LoginAttempt(
                email=email,
                ip_address=self._normalize_ip(ip_address),
                successful=False,
            )
        )
        db.commit()

    def clear(self, db: Session, email: str, ip_address: Optional[str]) -> None:
        normalized_ip = self._normalize_ip(ip_address)
        db.execute(
            delete(LoginAttempt).where(
                LoginAttempt.successful.is_(False),
                LoginAttempt.email == email,
                LoginAttempt.ip_address == normalized_ip,
            )
        )
        db.commit()


login_rate_limiter = LoginRateLimiter()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, payload: RegisterRequest) -> User:
        email = payload.email.lower()
        existing = self.db.scalar(select(User).where(User.email == email))
        if existing is not None:
            raise ConflictError("이미 가입된 이메일입니다.")
        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        normalized_email = email.lower()
        user = self.db.scalar(select(User).where(User.email == normalized_email))
        if user is None or not verify_password(password, user.password_hash):
            logger.warning("Authentication failed for email=%s", normalized_email)
            raise UnauthorizedError("이메일 또는 비밀번호가 올바르지 않습니다.")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

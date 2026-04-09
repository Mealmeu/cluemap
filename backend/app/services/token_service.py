from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int


class TokenService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _access_expiry(self) -> datetime:
        return self._now() + timedelta(minutes=self.settings.access_token_ttl_minutes)

    def _refresh_expiry(self) -> datetime:
        return self._now() + timedelta(days=self.settings.refresh_token_ttl_days)

    def _encode_access_token(self, user: User) -> tuple[str, datetime]:
        expires_at = self._access_expiry()
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "exp": expires_at,
            "iat": self._now(),
        }
        token = jwt.encode(payload, self.settings.access_token_secret, algorithm=self.settings.jwt_algorithm)
        return token, expires_at

    def _encode_refresh_token(self, user: User) -> tuple[str, datetime]:
        expires_at = self._refresh_expiry()
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "refresh",
            "jti": secrets.token_urlsafe(24),
            "exp": expires_at,
            "iat": self._now(),
        }
        token = jwt.encode(payload, self.settings.refresh_token_secret, algorithm=self.settings.jwt_algorithm)
        return token, expires_at

    def issue_tokens(self, user: User, user_agent: Optional[str], ip_address: Optional[str]) -> IssuedTokens:
        access_token, access_expires_at = self._encode_access_token(user)
        refresh_token, refresh_expires_at = self._encode_refresh_token(user)
        record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(record)
        self.db.commit()
        return IssuedTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=max(int((access_expires_at - self._now()).total_seconds()), 1),
        )

    def decode_access_token(self, token: str) -> dict[str, object]:
        try:
            payload = jwt.decode(
                token,
                self.settings.access_token_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("유효하지 않은 액세스 토큰입니다.") from exc
        if payload.get("type") != "access":
            raise UnauthorizedError("유효하지 않은 액세스 토큰입니다.")
        return payload

    def revoke_user_refresh_tokens(self, user_id: int) -> None:
        self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=self._now())
        )
        self.db.commit()

    def validate_refresh_token(
        self,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RefreshToken:
        try:
            payload = jwt.decode(
                refresh_token,
                self.settings.refresh_token_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            logger.warning("Invalid refresh token decode failed from ip=%s", ip_address)
            raise UnauthorizedError("유효하지 않은 리프레시 토큰입니다.") from exc
        if payload.get("type") != "refresh":
            logger.warning("Refresh token with invalid type from ip=%s", ip_address)
            raise UnauthorizedError("유효하지 않은 리프레시 토큰입니다.")
        record = self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_token))
        )
        if record is None:
            logger.warning("Refresh token record not found from ip=%s", ip_address)
            raise UnauthorizedError("유효하지 않은 리프레시 토큰입니다.")
        if record.revoked_at is not None:
            logger.warning("Revoked refresh token reuse detected for user_id=%s ip=%s", record.user_id, ip_address)
            self.revoke_user_refresh_tokens(record.user_id)
            raise UnauthorizedError("이미 폐기된 리프레시 토큰입니다. 다시 로그인해 주세요.")
        if record.expires_at <= self._now():
            logger.info("Expired refresh token rejected for user_id=%s ip=%s", record.user_id, ip_address)
            raise UnauthorizedError("만료된 리프레시 토큰입니다. 다시 로그인해 주세요.")
        if user_agent and record.user_agent and user_agent != record.user_agent:
            logger.warning("Refresh token user-agent changed for user_id=%s", record.user_id)
            record.revoked_at = self._now()
            self.db.add(record)
            self.db.commit()
            raise UnauthorizedError("세션 정보가 일치하지 않습니다. 다시 로그인해 주세요.")
        return record

    def revoke_refresh_token(self, refresh_token: Optional[str]) -> None:
        if not refresh_token:
            return
        record = self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(refresh_token))
        )
        if record is None or record.revoked_at is not None:
            return
        record.revoked_at = self._now()
        self.db.add(record)
        self.db.commit()

    def rotate_refresh_token(
        self,
        refresh_token: str,
        user_agent: Optional[str],
        ip_address: Optional[str],
    ) -> tuple[User, IssuedTokens]:
        record = self.validate_refresh_token(refresh_token, user_agent, ip_address)
        record.revoked_at = self._now()
        self.db.add(record)
        self.db.commit()
        user = self.db.get(User, record.user_id)
        if user is None:
            raise UnauthorizedError("사용자를 찾을 수 없습니다.")
        return user, self.issue_tokens(user, user_agent, ip_address)

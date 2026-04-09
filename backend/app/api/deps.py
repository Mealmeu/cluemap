from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.db.session import get_db
from app.models.user import User
from app.services.token_service import TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    if not token:
        raise UnauthorizedError("로그인이 필요합니다.")
    token_service = TokenService(db)
    payload = token_service.decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("유효하지 않은 사용자 정보입니다.")
    user = db.get(User, int(user_id))
    if user is None:
        raise UnauthorizedError("사용자를 찾을 수 없습니다.")
    return user


def require_role(*roles: str) -> Callable[[User], User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError()
        return user

    return dependency

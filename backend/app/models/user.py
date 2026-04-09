from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.problem import Problem
    from app.models.refresh_token import RefreshToken
    from app.models.submission import Submission


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")

    refresh_tokens: Mapped[list] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[list] = relationship(back_populates="user", cascade="all, delete-orphan")
    created_problems: Mapped[list] = relationship(back_populates="creator")

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.test_case import TestCase
    from app.models.user import User
    from app.models.submission import Submission


class Problem(TimestampMixin, Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    reference_solution_summary: Mapped[str] = mapped_column(Text, nullable=False)
    concept_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    misconception_taxonomy: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    creator: Mapped[object] = relationship(back_populates="created_problems")
    test_cases: Mapped[list] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="TestCase.order_index",
    )
    submissions: Mapped[list] = relationship(back_populates="problem", cascade="all, delete-orphan")

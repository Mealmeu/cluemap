from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis_result import AnalysisResult
    from app.models.problem import Problem
    from app.models.user import User


class Submission(TimestampMixin, Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    run_status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    passed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stdout_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stderr_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    failure_summary: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    improved: Mapped[Optional[bool]] = mapped_column(nullable=True)

    user: Mapped[object] = relationship(back_populates="submissions")
    problem: Mapped[object] = relationship(back_populates="submissions")
    analysis_result: Mapped[object] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        uselist=False,
    )

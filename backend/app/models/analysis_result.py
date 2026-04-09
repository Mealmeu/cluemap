from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow

if TYPE_CHECKING:
    from app.models.submission import Submission


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    student_state: Mapped[str] = mapped_column(Text, nullable=False)
    why_wrong: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    hint_level_1: Mapped[str] = mapped_column(Text, nullable=False)
    hint_level_2: Mapped[str] = mapped_column(Text, nullable=False)
    review_topics: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    teacher_summary: Mapped[str] = mapped_column(Text, nullable=False)
    analysis_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    submission: Mapped[object] = relationship(back_populates="analysis_result")

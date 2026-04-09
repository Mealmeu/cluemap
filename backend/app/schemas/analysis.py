from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AnalysisResultRead(ORMModel):
    id: int
    submission_id: int
    category: str
    confidence: float
    student_state: str
    why_wrong: str
    evidence: list[str]
    hint_level_1: str
    hint_level_2: str
    review_topics: list[str]
    teacher_summary: str
    analysis_version: str
    created_at: datetime


class AnalysisPayload(BaseModel):
    category: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    student_state: str = Field(min_length=1)
    why_wrong: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    hint_level_1: str = Field(min_length=1)
    hint_level_2: str = Field(min_length=1)
    review_topics: list[str] = Field(default_factory=list)
    teacher_summary: str = Field(min_length=1)

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResultRead
from app.schemas.common import ORMModel


class SubmissionCreate(BaseModel):
    problem_id: int
    code: str = Field(min_length=1, max_length=20000)


class SubmissionRead(ORMModel):
    id: int
    user_id: int
    problem_id: int
    code: str
    run_status: str
    passed_count: int
    total_count: int
    score: float
    stdout_excerpt: Optional[str]
    stderr_excerpt: Optional[str]
    failure_summary: list[dict[str, Any]]
    execution_time_ms: Optional[int]
    improved: Optional[bool]
    created_at: datetime
    updated_at: datetime
    analysis_result: Optional[AnalysisResultRead] = None


class SubmissionListResponse(BaseModel):
    items: list[SubmissionRead]

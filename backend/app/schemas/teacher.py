from typing import Optional

from datetime import datetime

from pydantic import BaseModel


class CategoryCount(BaseModel):
    category: str
    count: int


class RepeatedFailureStudent(BaseModel):
    student_id: int
    email: str
    failure_count: int
    latest_submission_at: Optional[datetime]


class TeacherProblemStats(BaseModel):
    problem_id: int
    total_submissions: int
    passed_submissions: int
    failed_submissions: int
    average_score: float
    misconception_distribution: list[CategoryCount]
    repeated_failures: list[RepeatedFailureStudent]


class TeacherProblemInsights(BaseModel):
    problem_id: int
    summary: str
    focus_points: list[str]
    review_topics: list[str]
    teacher_summaries: list[str]


class StudentHistoryItem(BaseModel):
    submission_id: int
    problem_id: int
    problem_title: str
    run_status: str
    score: float
    category: Optional[str]
    created_at: datetime


class StudentHistoryResponse(BaseModel):
    student_id: int
    items: list[StudentHistoryItem]

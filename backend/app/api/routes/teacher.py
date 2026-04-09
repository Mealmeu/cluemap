from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.teacher import StudentHistoryResponse, TeacherProblemInsights, TeacherProblemStats
from app.services.teacher_dashboard_service import TeacherDashboardService

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/problems/{problem_id}/stats", response_model=TeacherProblemStats)
def get_problem_stats(
    problem_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> TeacherProblemStats:
    return TeacherDashboardService(db).get_problem_stats(problem_id)


@router.get("/problems/{problem_id}/insights", response_model=TeacherProblemInsights)
def get_problem_insights(
    problem_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> TeacherProblemInsights:
    return TeacherDashboardService(db).get_problem_insights(problem_id)


@router.get("/students/{student_id}/history", response_model=StudentHistoryResponse)
def get_student_history(
    student_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> StudentHistoryResponse:
    return TeacherDashboardService(db).get_student_history(student_id)

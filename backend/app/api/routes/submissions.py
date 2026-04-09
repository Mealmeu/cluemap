from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.analysis import AnalysisResultRead
from app.schemas.submission import SubmissionCreate, SubmissionListResponse, SubmissionRead
from app.services.submission_service import SubmissionService

router = APIRouter(tags=["submissions"])


def _ensure_submission_access(current_user: User, submission) -> None:
    if current_user.role == "teacher":
        return
    if submission.user_id != current_user.id:
        raise ForbiddenError()


def _serialize_analysis(current_user: User, analysis) -> AnalysisResultRead:
    payload = AnalysisResultRead.model_validate(analysis)
    if current_user.role != "teacher":
        payload = payload.model_copy(update={"teacher_summary": ""})
    return payload


def _serialize_submission(current_user: User, submission) -> SubmissionRead:
    payload = SubmissionRead.model_validate(submission)
    if payload.analysis_result is not None and current_user.role != "teacher":
        payload = payload.model_copy(
            update={
                "analysis_result": payload.analysis_result.model_copy(update={"teacher_summary": ""}),
            }
        )
    return payload


@router.post("/submissions", response_model=SubmissionRead, status_code=201)
def create_submission(
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionRead:
    submission = SubmissionService(db).create_submission(current_user, payload)
    return _serialize_submission(current_user, submission)


@router.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionRead:
    submission = SubmissionService(db).get_submission(submission_id)
    _ensure_submission_access(current_user, submission)
    return _serialize_submission(current_user, submission)


@router.get("/submissions/{submission_id}/analysis", response_model=AnalysisResultRead)
def get_submission_analysis(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisResultRead:
    submission = SubmissionService(db).get_submission(submission_id)
    _ensure_submission_access(current_user, submission)
    if submission.analysis_result is None:
        raise NotFoundError("분석 결과를 찾을 수 없습니다.")
    return _serialize_analysis(current_user, submission.analysis_result)


@router.get("/problems/{problem_id}/submissions/me", response_model=SubmissionListResponse)
def get_my_problem_submissions(
    problem_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmissionListResponse:
    items = SubmissionService(db).list_user_problem_submissions(current_user.id, problem_id)
    return SubmissionListResponse(items=[_serialize_submission(current_user, item) for item in items])

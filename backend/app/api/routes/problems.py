from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.problem import ProblemCreate, ProblemListItem, ProblemRead, ProblemUpdate
from app.services.problem_service import ProblemService

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[ProblemListItem])
def list_problems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProblemListItem]:
    problems = ProblemService(db).list_problems()
    return [ProblemListItem.model_validate(problem) for problem in problems]


@router.get("/{problem_id}", response_model=ProblemRead)
def get_problem(
    problem_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProblemRead:
    service = ProblemService(db)
    problem = service.get_problem(problem_id)
    return service.serialize_problem(problem, include_hidden=current_user.role == "teacher")


@router.post("", response_model=ProblemRead, status_code=status.HTTP_201_CREATED)
def create_problem(
    payload: ProblemCreate,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> ProblemRead:
    service = ProblemService(db)
    problem = service.create_problem(payload, current_user.id)
    return service.serialize_problem(problem, include_hidden=True)


@router.put("/{problem_id}", response_model=ProblemRead)
def update_problem(
    problem_id: int,
    payload: ProblemUpdate,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> ProblemRead:
    service = ProblemService(db)
    problem = service.update_problem(problem_id, payload)
    return service.serialize_problem(problem, include_hidden=True)


@router.delete("/{problem_id}", response_model=MessageResponse)
def delete_problem(
    problem_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db),
) -> MessageResponse:
    ProblemService(db).delete_problem(problem_id)
    return MessageResponse(message="문제가 삭제되었습니다.")

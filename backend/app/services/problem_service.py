from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.schemas.problem import ProblemCreate, ProblemRead, ProblemUpdate, TestCaseRead


class ProblemService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_problems(self) -> list[Problem]:
        return list(self.db.scalars(select(Problem).order_by(Problem.id)).all())

    def get_problem(self, problem_id: int) -> Problem:
        statement = (
            select(Problem)
            .options(joinedload(Problem.test_cases))
            .where(Problem.id == problem_id)
        )
        problem = self.db.execute(statement).unique().scalar_one_or_none()
        if problem is None:
            raise NotFoundError("문제를 찾을 수 없습니다.")
        return problem

    def create_problem(self, payload: ProblemCreate, created_by: Optional[int]) -> Problem:
        problem = Problem(
            title=payload.title,
            description=payload.description,
            starter_code=payload.starter_code,
            reference_solution_summary=payload.reference_solution_summary,
            concept_tags=payload.concept_tags,
            misconception_taxonomy=payload.misconception_taxonomy,
            created_by=created_by,
        )
        for item in payload.test_cases:
            problem.test_cases.append(
                TestCase(
                    input_data=item.input_data,
                    expected_output=item.expected_output,
                    is_hidden=item.is_hidden,
                    order_index=item.order_index,
                )
            )
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return self.get_problem(problem.id)

    def update_problem(self, problem_id: int, payload: ProblemUpdate) -> Problem:
        problem = self.get_problem(problem_id)
        update_data = payload.model_dump(exclude_unset=True)
        test_cases = update_data.pop("test_cases", None)
        for key, value in update_data.items():
            setattr(problem, key, value)
        if test_cases is not None:
            problem.test_cases.clear()
            for item in test_cases:
                problem.test_cases.append(
                    TestCase(
                        input_data=item.input_data,
                        expected_output=item.expected_output,
                        is_hidden=item.is_hidden,
                        order_index=item.order_index,
                    )
                )
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return self.get_problem(problem.id)

    def delete_problem(self, problem_id: int) -> None:
        problem = self.get_problem(problem_id)
        self.db.delete(problem)
        self.db.commit()

    def serialize_problem(self, problem: Problem, include_hidden: bool) -> ProblemRead:
        test_cases = []
        for test_case in sorted(problem.test_cases, key=lambda item: item.order_index):
            expected_output = test_case.expected_output if include_hidden or not test_case.is_hidden else None
            test_cases.append(
                TestCaseRead(
                    id=test_case.id,
                    input_data=test_case.input_data,
                    expected_output=expected_output,
                    is_hidden=test_case.is_hidden,
                    order_index=test_case.order_index,
                )
            )
        return ProblemRead(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            starter_code=problem.starter_code,
            reference_solution_summary=problem.reference_solution_summary,
            concept_tags=list(problem.concept_tags or []),
            misconception_taxonomy=list(problem.misconception_taxonomy or []),
            created_by=problem.created_by,
            created_at=problem.created_at,
            updated_at=problem.updated_at,
            test_cases=test_cases,
        )

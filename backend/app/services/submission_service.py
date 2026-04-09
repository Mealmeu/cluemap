from __future__ import annotations

import hashlib

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.analysis_result import AnalysisResult
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.user import User
from app.schemas.submission import SubmissionCreate
from app.services.analysis_orchestration_service import AnalysisOrchestrationService
from app.services.problem_service import ProblemService
from app.services.sandbox_service import SandboxExecutionResult, SandboxService
from app.services.static_analysis_service import StaticAnalysisService


class SubmissionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.problem_service = ProblemService(db)
        self.static_analysis_service = StaticAnalysisService()
        self.sandbox_service = SandboxService()
        self.analysis_service = AnalysisOrchestrationService()

    def create_submission(self, user: User, payload: SubmissionCreate) -> Submission:
        if len(payload.code) > self.settings.max_submission_code_size:
            raise BadRequestError("제출 가능한 코드 길이를 초과했습니다.")

        problem = self.problem_service.get_problem(payload.problem_id)
        previous_submission = self.db.scalar(
            select(Submission)
            .where(Submission.user_id == user.id, Submission.problem_id == problem.id)
            .order_by(desc(Submission.created_at))
            .limit(1)
        )

        static_signals = self.static_analysis_service.analyze(payload.code)
        submission = Submission(
            user_id=user.id,
            problem_id=problem.id,
            code=payload.code,
            code_hash=hashlib.sha256(payload.code.encode("utf-8")).hexdigest(),
            run_status="running",
            total_count=len(problem.test_cases),
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        execution_result = self._execute(problem, payload.code, static_signals)
        submission.run_status = execution_result.run_status
        submission.passed_count = execution_result.passed_count
        submission.total_count = execution_result.total_count
        submission.score = execution_result.score
        submission.stdout_excerpt = execution_result.stdout_excerpt
        submission.stderr_excerpt = execution_result.stderr_excerpt
        submission.failure_summary = execution_result.failure_summary
        submission.execution_time_ms = execution_result.execution_time_ms
        submission.improved = None if previous_submission is None else execution_result.score > previous_submission.score

        analysis_payload = self.analysis_service.analyze(
            problem=problem,
            code=payload.code,
            static_signals=static_signals,
            execution_result=execution_result,
        )
        analysis = AnalysisResult(
            submission_id=submission.id,
            category=analysis_payload.category,
            confidence=analysis_payload.confidence,
            student_state=analysis_payload.student_state,
            why_wrong=analysis_payload.why_wrong,
            evidence=analysis_payload.evidence,
            hint_level_1=analysis_payload.hint_level_1,
            hint_level_2=analysis_payload.hint_level_2,
            review_topics=analysis_payload.review_topics,
            teacher_summary=analysis_payload.teacher_summary,
            analysis_version=self.settings.analysis_version,
        )
        self.db.add(submission)
        self.db.add(analysis)
        self.db.commit()
        return self.get_submission(submission.id)

    def _execute(
        self,
        problem: Problem,
        code: str,
        static_signals: dict[str, object],
    ) -> SandboxExecutionResult:
        if static_signals.get("syntax_error"):
            message = f"문법 오류: {static_signals.get('syntax_message')}"
            return self.sandbox_service.create_non_executed_result("syntax_error", message, len(problem.test_cases))
        if static_signals.get("banned_imports"):
            imports = ", ".join(static_signals.get("banned_imports", []))
            return self.sandbox_service.create_non_executed_result(
                "blocked",
                f"허용되지 않은 import가 포함되어 있습니다: {imports}",
                len(problem.test_cases),
            )
        if static_signals.get("dangerous_calls"):
            calls = ", ".join(static_signals.get("dangerous_calls", []))
            return self.sandbox_service.create_non_executed_result(
                "blocked",
                f"허용되지 않은 함수 호출이 포함되어 있습니다: {calls}",
                len(problem.test_cases),
            )
        if static_signals.get("dunder_access"):
            return self.sandbox_service.create_non_executed_result(
                "blocked",
                "이중 밑줄 기반 접근은 허용되지 않습니다.",
                len(problem.test_cases),
            )
        return self.sandbox_service.execute(problem, code, list(problem.test_cases))

    def get_submission(self, submission_id: int) -> Submission:
        statement = (
            select(Submission)
            .options(
                joinedload(Submission.analysis_result),
                joinedload(Submission.problem),
                joinedload(Submission.user),
            )
            .where(Submission.id == submission_id)
        )
        submission = self.db.execute(statement).unique().scalar_one_or_none()
        if submission is None:
            raise NotFoundError("제출을 찾을 수 없습니다.")
        return submission

    def list_user_problem_submissions(self, user_id: int, problem_id: int) -> list[Submission]:
        statement = (
            select(Submission)
            .options(joinedload(Submission.analysis_result))
            .where(Submission.user_id == user_id, Submission.problem_id == problem_id)
            .order_by(desc(Submission.created_at))
        )
        return list(self.db.execute(statement).unique().scalars().all())

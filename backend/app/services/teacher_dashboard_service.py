from __future__ import annotations

from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.models.problem import Problem
from app.models.submission import Submission
from app.schemas.teacher import (
    CategoryCount,
    RepeatedFailureStudent,
    StudentHistoryItem,
    StudentHistoryResponse,
    TeacherProblemInsights,
    TeacherProblemStats,
)


class TeacherDashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def get_problem_stats(self, problem_id: int) -> TeacherProblemStats:
        problem = self.db.get(Problem, problem_id)
        if problem is None:
            raise NotFoundError("문제를 찾을 수 없습니다.")

        submissions = list(
            self.db.execute(
                select(Submission)
                .options(joinedload(Submission.user), joinedload(Submission.analysis_result))
                .where(Submission.problem_id == problem_id)
            )
            .unique()
            .scalars()
            .all()
        )

        total_submissions = len(submissions)
        passed_submissions = sum(1 for item in submissions if item.run_status == "passed")
        failed_submissions = sum(1 for item in submissions if item.run_status != "passed")
        average_score = round(sum(item.score for item in submissions) / total_submissions, 4) if total_submissions else 0.0

        category_counter = Counter(
            item.analysis_result.category
            for item in submissions
            if item.analysis_result is not None
        )
        misconception_distribution = [
            CategoryCount(category=category, count=count)
            for category, count in category_counter.most_common()
        ]

        failures_by_student: dict[int, list[Submission]] = defaultdict(list)
        for item in submissions:
            if item.run_status != "passed":
                failures_by_student[item.user_id].append(item)

        repeated_failures = []
        for student_id, items in failures_by_student.items():
            if len(items) < 2:
                continue
            latest = max(items, key=lambda entry: entry.created_at)
            repeated_failures.append(
                RepeatedFailureStudent(
                    student_id=student_id,
                    email=latest.user.email,
                    failure_count=len(items),
                    latest_submission_at=latest.created_at,
                )
            )
        repeated_failures.sort(key=lambda item: (-item.failure_count, item.email))

        return TeacherProblemStats(
            problem_id=problem_id,
            total_submissions=total_submissions,
            passed_submissions=passed_submissions,
            failed_submissions=failed_submissions,
            average_score=average_score,
            misconception_distribution=misconception_distribution,
            repeated_failures=repeated_failures,
        )

    def get_problem_insights(self, problem_id: int) -> TeacherProblemInsights:
        problem = self.db.get(Problem, problem_id)
        if problem is None:
            raise NotFoundError("문제를 찾을 수 없습니다.")

        submissions = list(
            self.db.execute(
                select(Submission)
                .options(joinedload(Submission.analysis_result))
                .where(Submission.problem_id == problem_id)
            )
            .unique()
            .scalars()
            .all()
        )
        analyses = [item.analysis_result for item in submissions if item.analysis_result is not None]
        category_counter = Counter(item.category for item in analyses)
        review_topic_counter = Counter(topic for item in analyses for topic in item.review_topics or [])
        teacher_summaries = [item.teacher_summary for item in analyses[:5]]
        if category_counter:
            top_category, top_count = category_counter.most_common(1)[0]
            summary = f"총 {len(submissions)}건의 제출 중 가장 많은 오답 유형은 {top_category}이며 {top_count}건입니다."
        else:
            summary = "아직 집계할 제출 데이터가 없습니다."
        focus_points = [f"{category} 유형 비중이 높습니다." for category, _ in category_counter.most_common(3)]
        review_topics = [topic for topic, _ in review_topic_counter.most_common(self.settings.teacher_focus_topic_limit)]

        return TeacherProblemInsights(
            problem_id=problem_id,
            summary=summary,
            focus_points=focus_points,
            review_topics=review_topics,
            teacher_summaries=teacher_summaries,
        )

    def get_student_history(self, student_id: int) -> StudentHistoryResponse:
        submissions = list(
            self.db.execute(
                select(Submission)
                .options(joinedload(Submission.problem), joinedload(Submission.analysis_result))
                .where(Submission.user_id == student_id)
                .order_by(Submission.created_at.desc())
            )
            .unique()
            .scalars()
            .all()
        )

        return StudentHistoryResponse(
            student_id=student_id,
            items=[
                StudentHistoryItem(
                    submission_id=item.id,
                    problem_id=item.problem_id,
                    problem_title=item.problem.title,
                    run_status=item.run_status,
                    score=item.score,
                    category=item.analysis_result.category if item.analysis_result else None,
                    created_at=item.created_at,
                )
                for item in submissions
            ],
        )

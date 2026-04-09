from __future__ import annotations

from app.models.problem import Problem
from app.schemas.analysis import AnalysisPayload
from app.services.llm_service import LLMService
from app.services.rule_engine import RuleEngine
from app.services.sandbox_service import SandboxExecutionResult


class AnalysisOrchestrationService:
    def __init__(self) -> None:
        self.rule_engine = RuleEngine()
        self.llm_service = LLMService()

    def analyze(
        self,
        problem: Problem,
        code: str,
        static_signals: dict[str, object],
        execution_result: SandboxExecutionResult,
    ) -> AnalysisPayload:
        rule_based_analysis = self.rule_engine.classify(problem, static_signals, execution_result)
        return self.llm_service.analyze(
            problem_payload={
                "title": problem.title,
                "description": problem.description,
                "concept_tags": problem.concept_tags,
                "misconception_taxonomy": problem.misconception_taxonomy,
                "reference_solution_summary": problem.reference_solution_summary,
            },
            code=code,
            static_signals=static_signals,
            execution_result=execution_result,
            rule_based_analysis=rule_based_analysis,
        )

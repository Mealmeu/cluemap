from __future__ import annotations

from dataclasses import dataclass

from app.models.problem import Problem
from app.services.sandbox_service import SandboxExecutionResult


@dataclass
class RuleBasedAnalysis:
    category: str
    confidence: float
    student_state: str
    why_wrong: str
    evidence: list[str]
    hint_level_1: str
    hint_level_2: str
    review_topics: list[str]
    teacher_summary: str


class RuleEngine:
    def classify(
        self,
        problem: Problem,
        static_signals: dict[str, object],
        execution_result: SandboxExecutionResult,
    ) -> RuleBasedAnalysis:
        title = problem.title
        concept_tags = {item.lower() for item in problem.concept_tags or []}

        if static_signals.get("syntax_error"):
            return RuleBasedAnalysis(
                category="syntax_error",
                confidence=0.98,
                student_state="문법 단계에서 코드 구조를 아직 안정적으로 작성하지 못하고 있습니다.",
                why_wrong="괄호, 콜론, 들여쓰기 또는 함수 정의 문법이 맞지 않아 코드가 실행되기 전에 멈췄습니다.",
                evidence=[f"syntax: {static_signals.get('syntax_message')}"],
                hint_level_1="오류가 난 줄 근처에서 괄호, 콜론, 들여쓰기를 먼저 다시 확인해 보세요.",
                hint_level_2="starter code의 함수 정의 줄과 return 위치를 기준으로 줄 수를 하나씩 맞춰 보세요.",
                review_topics=["함수 정의 문법", "들여쓰기", "콜론과 괄호"],
                teacher_summary="문법 오류가 선행되어 개념 분석보다 기본 Python 문법 복습이 우선입니다.",
            )

        if static_signals.get("banned_imports"):
            imports = ", ".join(static_signals.get("banned_imports", []))
            return RuleBasedAnalysis(
                category="runtime_error",
                confidence=0.95,
                student_state="문제를 푸는 핵심 로직보다 허용되지 않은 모듈 사용에 의존하고 있습니다.",
                why_wrong=f"보안 정책상 허용되지 않은 import가 포함되어 실행이 차단되었습니다: {imports}",
                evidence=[f"banned_imports: {imports}"],
                hint_level_1="별도 모듈 없이 반복문과 조건문, 변수만으로 문제를 해결해 보세요.",
                hint_level_2="starter code 기준으로 입력을 순회하고 직접 값을 누적하거나 비교하는 방식으로 바꿔 보세요.",
                review_topics=["기본 제어문", "문제 해석", "함수 구현"],
                teacher_summary="보안 차단 케이스입니다. 문제 해결보다 환경 우회 시도가 먼저 나타났습니다.",
            )

        if static_signals.get("dangerous_calls") or static_signals.get("dunder_access"):
            return RuleBasedAnalysis(
                category="runtime_error",
                confidence=0.96,
                student_state="기본 문제 해결과 무관한 위험 기능을 사용하려고 했습니다.",
                why_wrong="교육용 샌드박스에서는 파일 접근, 동적 실행, 내부 속성 우회 같은 기능이 차단됩니다.",
                evidence=["dangerous_runtime_access"],
                hint_level_1="문제 해결에 필요한 것은 함수, 반복문, 조건문, 변수 정도라는 점을 떠올려 보세요.",
                hint_level_2="외부 기능을 쓰지 말고 입력을 직접 순회하면서 답을 계산하는 구조로 다시 작성해 보세요.",
                review_topics=["기본 문법으로 해결하기", "반복문", "조건문"],
                teacher_summary="샌드박스 우회 성격의 접근이 감지되었습니다. 기본 문법으로 해결하도록 유도할 필요가 있습니다.",
            )

        if execution_result.run_status in {"timeout", "runtime_error"}:
            error = execution_result.stderr_excerpt or "실행 중 오류"
            return RuleBasedAnalysis(
                category="runtime_error",
                confidence=0.9,
                student_state="개념은 일부 시도했지만 실행 중 예외 처리나 종료 조건이 안정적이지 않습니다.",
                why_wrong=f"코드가 실행 중 멈추거나 예외가 발생했습니다: {error}",
                evidence=[error],
                hint_level_1="함수에 전달되는 입력 형태와 변수 초기값을 먼저 손으로 적어 보세요.",
                hint_level_2="반복문 종료 조건, 인덱스 접근 범위, 초기값 설정을 한 줄씩 점검해 보세요.",
                review_topics=["초기값", "인덱스 범위", "반복 종료 조건"],
                teacher_summary="실행 중 예외 또는 무한 루프 성격의 실패입니다. 입력 형태와 종료 조건 점검이 필요합니다.",
            )

        if execution_result.run_status == "passed":
            return RuleBasedAnalysis(
                category="partial_understanding",
                confidence=0.75,
                student_state="현재 제출은 테스트를 통과했습니다.",
                why_wrong="현재 제출은 주어진 테스트 기준으로 올바르게 동작합니다.",
                evidence=["all_visible_and_hidden_tests_passed"],
                hint_level_1="왜 이 코드가 맞는지 입력, 반복, 조건, 반환 흐름으로 설명해 보세요.",
                hint_level_2="다른 입력 예시를 넣었을 때도 같은 방식으로 동작하는지 스스로 추적해 보세요.",
                review_topics=["문제 풀이 설명", "함수 반환값", "조건과 반복 연결"],
                teacher_summary="현재 제출은 통과 상태입니다. 설명 가능성과 개념 정착 여부를 확인하면 좋습니다.",
            )

        if "짝수" in title and not static_signals.get("has_if"):
            return RuleBasedAnalysis(
                category="wrong_condition_logic",
                confidence=0.86,
                student_state="반복은 시도했지만 짝수만 골라내는 조건이 비어 있을 가능성이 큽니다.",
                why_wrong="리스트를 순회하더라도 짝수 조건 없이 모두 더하면 정답과 달라집니다.",
                evidence=["problem_requires_even_filter", f"has_if={static_signals.get('has_if')}"],
                hint_level_1="수를 더하기 전에 이 수가 짝수인지 먼저 확인해야 합니다.",
                hint_level_2="나머지가 0인지 검사하는 조건문이 반복문 안에 있는지 확인해 보세요.",
                review_topics=["조건문", "나머지 연산", "누적 변수"],
                teacher_summary="짝수 필터링 조건 누락 가능성이 큽니다.",
            )

        if "모음" in title and not static_signals.get("has_if"):
            return RuleBasedAnalysis(
                category="wrong_condition_logic",
                confidence=0.86,
                student_state="문자를 돌고 있지만 모음인지 판단하는 조건이 약합니다.",
                why_wrong="문자를 하나씩 보더라도 모음인지 확인하지 않으면 개수를 정확히 셀 수 없습니다.",
                evidence=["problem_requires_vowel_filter", f"has_if={static_signals.get('has_if')}"],
                hint_level_1="문자를 셀 때는 모든 글자를 세는 것이 아니라 모음만 세야 합니다.",
                hint_level_2="현재 문자가 a, e, i, o, u 중 하나인지 검사하는 조건이 있는지 확인해 보세요.",
                review_topics=["문자 순회", "조건문", "카운터"],
                teacher_summary="모음 판별 조건 누락 가능성이 큽니다.",
            )

        if "최댓값" in title and not static_signals.get("has_if") and not static_signals.get("has_max_call"):
            return RuleBasedAnalysis(
                category="loop_scope_error",
                confidence=0.82,
                student_state="리스트를 돌더라도 현재 최댓값과 비교하는 기준이 부족합니다.",
                why_wrong="최댓값 문제는 현재 값보다 큰 수를 만나면 기준값을 갱신해야 합니다.",
                evidence=["problem_requires_max_compare", f"has_if={static_signals.get('has_if')}"],
                hint_level_1="지금까지 본 값 중 가장 큰 값을 저장할 변수가 필요합니다.",
                hint_level_2="반복문 안에서 현재 원소와 저장된 최댓값을 비교하고 더 크면 바꾸는지 확인해 보세요.",
                review_topics=["비교 연산", "상태 갱신", "반복문"],
                teacher_summary="최댓값 갱신 패턴이 부족합니다.",
            )

        if "accumulator" in concept_tags and not static_signals.get("has_accumulator") and not static_signals.get("has_sum_call"):
            return RuleBasedAnalysis(
                category="accumulator_missing",
                confidence=0.83,
                student_state="값을 모으는 누적 변수 개념이 아직 흔들리고 있습니다.",
                why_wrong="반복 중 결과를 저장하고 갱신할 변수가 없으면 최종 답을 만들기 어렵습니다.",
                evidence=["accumulator_missing_signal"],
                hint_level_1="반복문이 시작되기 전에 결과를 담을 변수를 먼저 준비해 보세요.",
                hint_level_2="반복문 안에서 그 변수를 어떻게 바꿔야 하는지 한 줄로 써 보세요.",
                review_topics=["누적 변수", "초기값", "반복문"],
                teacher_summary="누적 변수 패턴이 아직 안정적이지 않습니다.",
            )

        for failure in execution_result.failure_summary:
            actual_output = failure.get("actual_output")
            if actual_output is None and execution_result.stdout_excerpt:
                return RuleBasedAnalysis(
                    category="output_format_issue",
                    confidence=0.78,
                    student_state="계산보다 출력과 반환의 차이를 헷갈리고 있습니다.",
                    why_wrong="값을 return 해야 하는 자리에서 print만 사용하면 채점기는 결과를 받지 못합니다.",
                    evidence=["actual_output_none_with_stdout"],
                    hint_level_1="print와 return의 역할이 같은지 먼저 구분해 보세요.",
                    hint_level_2="함수가 실제로 값을 돌려주고 있는지 마지막 줄을 확인해 보세요.",
                    review_topics=["return", "print", "함수 결과"],
                    teacher_summary="출력과 반환의 구분이 불안정합니다.",
                )

        return RuleBasedAnalysis(
            category="partial_understanding",
            confidence=0.7,
            student_state="핵심 개념 일부는 보이지만 정답으로 연결하는 마지막 구조가 아직 불안정합니다.",
            why_wrong="반복, 조건, 반환 중 하나 이상이 문제 요구와 완전히 연결되지 않았습니다.",
            evidence=["default_partial_understanding"],
            hint_level_1="문제가 요구하는 입력, 처리, 반환을 세 칸으로 나눠 적어 보세요.",
            hint_level_2="현재 코드에서 어떤 줄이 조건을 처리하고 어떤 줄이 결과를 만드는지 표시해 보세요.",
            review_topics=["문제 분해", "조건과 반복 연결", "반환값"],
            teacher_summary="부분 이해 상태입니다. 문제 요구를 코드 구조로 옮기는 연습이 더 필요합니다.",
        )

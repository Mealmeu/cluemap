from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.problem import Problem
from app.models.test_case import TestCase

SEED_PROBLEMS = [
    {
        "title": "리스트에서 짝수의 합 구하기",
        "description": "정수 리스트가 주어졌을 때 짝수인 값만 더한 결과를 반환하는 함수를 작성하세요.",
        "starter_code": "def sum_even_numbers(numbers):\n    total = 0\n    return total\n",
        "reference_solution_summary": "리스트를 순회하면서 각 원소가 짝수인지 확인하고, 짝수일 때만 total에 더한 뒤 반환합니다.",
        "concept_tags": ["loop", "condition", "accumulator", "function"],
        "misconception_taxonomy": ["wrong_condition_logic", "accumulator_missing", "output_format_issue"],
        "test_cases": [
            {"input_data": {"args": [[1, 2, 3, 4, 5, 6]]}, "expected_output": 12, "is_hidden": False, "order_index": 0},
            {"input_data": {"args": [[1, 3, 5]]}, "expected_output": 0, "is_hidden": False, "order_index": 1},
            {"input_data": {"args": [[2, 8, 10, 11]]}, "expected_output": 20, "is_hidden": True, "order_index": 2},
        ],
    },
    {
        "title": "문자열에서 모음 개수 세기",
        "description": "영문 소문자 문자열이 주어졌을 때 모음 a, e, i, o, u의 개수를 반환하는 함수를 작성하세요.",
        "starter_code": "def count_vowels(text):\n    count = 0\n    return count\n",
        "reference_solution_summary": "문자열을 한 글자씩 확인하면서 현재 문자가 모음 집합에 포함되면 count를 증가시킵니다.",
        "concept_tags": ["string", "loop", "condition", "accumulator"],
        "misconception_taxonomy": ["wrong_condition_logic", "accumulator_missing", "partial_understanding"],
        "test_cases": [
            {"input_data": {"args": ["education"]}, "expected_output": 5, "is_hidden": False, "order_index": 0},
            {"input_data": {"args": ["python"]}, "expected_output": 1, "is_hidden": False, "order_index": 1},
            {"input_data": {"args": ["queue"]}, "expected_output": 4, "is_hidden": True, "order_index": 2},
        ],
    },
    {
        "title": "리스트에서 최댓값 찾기",
        "description": "비어 있지 않은 정수 리스트가 주어졌을 때 가장 큰 값을 반환하는 함수를 작성하세요.",
        "starter_code": "def find_max(numbers):\n    current_max = numbers[0]\n    return current_max\n",
        "reference_solution_summary": "첫 번째 원소를 현재 최댓값으로 두고 나머지 원소를 순회하며 더 큰 값이 나오면 current_max를 갱신합니다.",
        "concept_tags": ["loop", "comparison", "state_update", "function"],
        "misconception_taxonomy": ["loop_scope_error", "runtime_error", "partial_understanding"],
        "test_cases": [
            {"input_data": {"args": [[3, 7, 2, 9, 4]]}, "expected_output": 9, "is_hidden": False, "order_index": 0},
            {"input_data": {"args": [[-5, -1, -9]]}, "expected_output": -1, "is_hidden": False, "order_index": 1},
            {"input_data": {"args": [[100, 20, 30, 99]]}, "expected_output": 100, "is_hidden": True, "order_index": 2},
        ],
    },
]


def seed() -> None:
    with SessionLocal() as db:
        for item in SEED_PROBLEMS:
            problem = db.scalar(select(Problem).where(Problem.title == item["title"]))
            if problem is None:
                problem = Problem(
                    title=item["title"],
                    description=item["description"],
                    starter_code=item["starter_code"],
                    reference_solution_summary=item["reference_solution_summary"],
                    concept_tags=item["concept_tags"],
                    misconception_taxonomy=item["misconception_taxonomy"],
                    created_by=None,
                )
                db.add(problem)
                db.flush()
            else:
                problem.description = item["description"]
                problem.starter_code = item["starter_code"]
                problem.reference_solution_summary = item["reference_solution_summary"]
                problem.concept_tags = item["concept_tags"]
                problem.misconception_taxonomy = item["misconception_taxonomy"]
                problem.test_cases.clear()
                db.add(problem)
                db.flush()
            for test_case in item["test_cases"]:
                problem.test_cases.append(TestCase(**test_case))
            db.add(problem)
        db.commit()


if __name__ == "__main__":
    seed()

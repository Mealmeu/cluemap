from __future__ import annotations

import http.cookiejar
import json
import os
import ssl
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Tuple


def contains_hangul(value: str) -> bool:
    return any("\uac00" <= ch <= "\ud7a3" for ch in value)


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class BrowserSession:
    def __init__(self, base_url: str, user_agent: str, insecure_tls: bool) -> None:
        self.base_url = base_url.rstrip("/")
        parsed = urllib.parse.urlparse(self.base_url)
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.cookie_jar = http.cookiejar.CookieJar()
        handlers: list[Any] = [urllib.request.HTTPCookieProcessor(self.cookie_jar)]
        if parsed.scheme == "https":
            context = ssl._create_unverified_context() if insecure_tls else ssl.create_default_context()
            handlers.append(urllib.request.HTTPSHandler(context=context))
        self.opener = urllib.request.build_opener(*handlers)
        self.user_agent = user_agent

    def csrf_token(self) -> Optional[str]:
        for cookie in self.cookie_jar:
            if cookie.name == "cluemap_csrf_token":
                return cookie.value
        return None

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[dict[str, Any]] = None,
        access_token: Optional[str] = None,
        include_csrf: bool = True,
        expected_statuses: Tuple[int, ...] = (200,),
    ) -> tuple[int, Any]:
        headers = {
            "Accept": "application/json",
            "Origin": self.origin,
            "User-Agent": self.user_agent,
            "Accept-Language": "ko-KR,ko;q=0.9",
        }
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        if include_csrf:
            csrf_token = self.csrf_token()
            if csrf_token:
                headers["X-CSRF-Token"] = csrf_token

        request = urllib.request.Request(
            url=f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            response = self.opener.open(request, timeout=30)
            status_code = response.getcode()
            body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            body = exc.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            raise AssertionError(f"요청 실패: {path} {exc}") from exc

        if status_code not in expected_statuses:
            raise AssertionError(f"예상하지 못한 상태 코드입니다: {method} {path} -> {status_code} {body}")

        if not body:
            return status_code, None

        try:
            return status_code, json.loads(body)
        except json.JSONDecodeError:
            return status_code, body


def make_email(prefix: str) -> str:
    return f"{prefix}-{int(time.time())}-{uuid.uuid4().hex[:8]}@example.com"


def main() -> None:
    base_url = os.getenv("CLUE_MAP_BASE_URL", "http://localhost").rstrip("/")
    insecure_tls = os.getenv("CLUE_MAP_INSECURE_TLS", "false").lower() in {"1", "true", "yes"}

    student_session = BrowserSession(base_url, "cluemap-smoke-student/1.0", insecure_tls)
    teacher_session = BrowserSession(base_url, "cluemap-smoke-teacher/1.0", insecure_tls)

    student_email = make_email("student")
    teacher_email = make_email("teacher")
    password = "Password123!"

    _, student_register = student_session.request(
        "POST",
        "/api/auth/register",
        payload={"email": student_email, "password": password, "role": "student"},
        include_csrf=False,
        expected_statuses=(201,),
    )
    student_access_token = student_register["access_token"]
    student_id = student_register["user"]["id"]
    expect(student_register["user"]["role"] == "student", "학생 회원가입 역할이 잘못되었습니다.")

    _, student_me = student_session.request("GET", "/api/auth/me", access_token=student_access_token)
    expect(student_me["email"] == student_email, "학생 auth/me 응답이 잘못되었습니다.")

    _, student_refresh = student_session.request("POST", "/api/auth/refresh")
    student_access_token = student_refresh["access_token"]

    _, student_logout = student_session.request("POST", "/api/auth/logout")
    expect(student_logout["message"] == "로그아웃되었습니다.", "학생 로그아웃 메시지가 예상과 다릅니다.")

    student_refresh_after_logout_status, _ = student_session.request(
        "POST",
        "/api/auth/refresh",
        expected_statuses=(401, 403),
    )
    expect(student_refresh_after_logout_status in {401, 403}, "로그아웃 후 refresh 차단이 동작하지 않습니다.")

    _, student_login = student_session.request(
        "POST",
        "/api/auth/login",
        payload={"email": student_email, "password": password},
        include_csrf=False,
    )
    student_access_token = student_login["access_token"]

    _, teacher_register = teacher_session.request(
        "POST",
        "/api/auth/register",
        payload={"email": teacher_email, "password": password, "role": "teacher"},
        include_csrf=False,
        expected_statuses=(201,),
    )
    teacher_access_token = teacher_register["access_token"]
    expect(teacher_register["user"]["role"] == "teacher", "교사 회원가입 역할이 잘못되었습니다.")

    teacher_session.request("POST", "/api/auth/logout")
    _, teacher_login = teacher_session.request(
        "POST",
        "/api/auth/login",
        payload={"email": teacher_email, "password": password},
        include_csrf=False,
    )
    teacher_access_token = teacher_login["access_token"]

    _, teacher_me = teacher_session.request("GET", "/api/auth/me", access_token=teacher_access_token)
    expect(teacher_me["email"] == teacher_email, "교사 auth/me 응답이 잘못되었습니다.")

    _, created_problem = teacher_session.request(
        "POST",
        "/api/problems",
        payload={
            "title": f"테스트 문제 {uuid.uuid4().hex[:6]}",
            "description": "리스트에서 짝수의 합을 구하는 함수를 작성하세요.",
            "starter_code": "def sum_even_numbers(numbers):\n    total = 0\n    return total\n",
            "reference_solution_summary": "짝수만 골라 누적 합을 구합니다.",
            "concept_tags": ["loop", "condition", "accumulator"],
            "misconception_taxonomy": ["wrong_condition_logic", "accumulator_missing"],
            "test_cases": [
                {
                    "input_data": {"args": [[1, 2, 3, 4]]},
                    "expected_output": 6,
                    "is_hidden": False,
                    "order_index": 0,
                },
                {
                    "input_data": {"args": [[2, 6, 8]]},
                    "expected_output": 16,
                    "is_hidden": True,
                    "order_index": 1,
                },
            ],
        },
        access_token=teacher_access_token,
        expected_statuses=(201,),
    )
    problem_id = created_problem["id"]

    _, problem_list = student_session.request("GET", "/api/problems", access_token=student_access_token)
    expect(any(item["id"] == problem_id for item in problem_list), "학생 문제 목록에서 생성한 문제를 찾지 못했습니다.")

    _, problem_detail = student_session.request(
        "GET",
        f"/api/problems/{problem_id}",
        access_token=student_access_token,
    )
    expect(problem_detail["title"] == created_problem["title"], "학생 문제 상세 제목이 일치하지 않습니다.")
    expect(problem_detail["test_cases"][1]["expected_output"] is None, "학생에게 hidden test 정답이 노출되었습니다.")

    _, good_submission = student_session.request(
        "POST",
        "/api/submissions",
        payload={
            "problem_id": problem_id,
            "code": "def sum_even_numbers(numbers):\n    total = 0\n    for number in numbers:\n        if number % 2 == 0:\n            total += number\n    return total\n",
        },
        access_token=student_access_token,
        expected_statuses=(201,),
    )
    expect(good_submission["run_status"] == "passed", "정상 제출이 통과하지 않았습니다.")
    expect(good_submission["analysis_result"]["category"], "분석 결과 category가 비어 있습니다.")
    expect(contains_hangul(good_submission["analysis_result"]["student_state"]), "student_state가 한국어가 아닙니다.")
    expect(contains_hangul(good_submission["analysis_result"]["why_wrong"]), "why_wrong이 한국어가 아닙니다.")
    expect(contains_hangul(good_submission["analysis_result"]["hint_level_1"]), "hint_level_1이 한국어가 아닙니다.")
    expect(good_submission["analysis_result"]["teacher_summary"] == "", "학생 응답에 teacher_summary가 노출되었습니다.")
    submission_id = good_submission["id"]

    _, submission_detail = student_session.request(
        "GET",
        f"/api/submissions/{submission_id}",
        access_token=student_access_token,
    )
    expect(submission_detail["id"] == submission_id, "제출 상세 조회가 잘못되었습니다.")

    _, analysis_detail = student_session.request(
        "GET",
        f"/api/submissions/{submission_id}/analysis",
        access_token=student_access_token,
    )
    expect(analysis_detail["teacher_summary"] == "", "학생 분석 조회에 teacher_summary가 노출되었습니다.")

    _, submission_history = student_session.request(
        "GET",
        f"/api/problems/{problem_id}/submissions/me",
        access_token=student_access_token,
    )
    expect(len(submission_history["items"]) >= 1, "학생 제출 이력이 비어 있습니다.")

    _, bad_submission = student_session.request(
        "POST",
        "/api/submissions",
        payload={
            "problem_id": problem_id,
            "code": "def sum_even_numbers(numbers):\n    return 999\n",
        },
        access_token=student_access_token,
        expected_statuses=(201,),
    )
    hidden_failures = [item for item in bad_submission["failure_summary"] if item.get("is_hidden")]
    expect(hidden_failures, "hidden test 실패가 검출되지 않았습니다.")
    expect(
        all("expected_output" not in item and "actual_output" not in item for item in hidden_failures),
        "hidden test 상세 결과가 과노출되었습니다.",
    )

    _, teacher_stats = teacher_session.request(
        "GET",
        f"/api/teacher/problems/{problem_id}/stats",
        access_token=teacher_access_token,
    )
    expect(teacher_stats["total_submissions"] >= 2, "교사 통계 제출 수가 예상보다 적습니다.")

    _, teacher_insights = teacher_session.request(
        "GET",
        f"/api/teacher/problems/{problem_id}/insights",
        access_token=teacher_access_token,
    )
    expect(contains_hangul(teacher_insights["summary"]), "교사 인사이트 요약이 한국어가 아닙니다.")

    _, teacher_history = teacher_session.request(
        "GET",
        f"/api/teacher/students/{student_id}/history",
        access_token=teacher_access_token,
    )
    expect(len(teacher_history["items"]) >= 2, "교사 학생 이력이 예상보다 적습니다.")

    student_block_status, _ = student_session.request(
        "GET",
        f"/api/teacher/problems/{problem_id}/stats",
        access_token=student_access_token,
        expected_statuses=(403,),
    )
    expect(student_block_status == 403, "학생의 교사 통계 접근이 차단되지 않았습니다.")

    print("ClueMap 검증 통과")
    print(f"base_url={base_url}")
    print(f"student_email={student_email}")
    print(f"teacher_email={teacher_email}")
    print(f"problem_id={problem_id}")
    print(f"submission_id={submission_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ClueMap 검증 실패: {exc}", file=sys.stderr)
        raise

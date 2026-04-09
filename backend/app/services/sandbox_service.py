from __future__ import annotations

import ast
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from app.core.config import get_settings
from app.core.runner_security import build_runner_headers
from app.models.problem import Problem
from app.models.test_case import TestCase

logger = logging.getLogger(__name__)


@dataclass
class SandboxExecutionResult:
    run_status: str
    passed_count: int
    total_count: int
    score: float
    stdout_excerpt: Optional[str]
    stderr_excerpt: Optional[str]
    failure_summary: list[dict[str, Any]]
    case_results: list[dict[str, Any]]
    execution_time_ms: Optional[int]


class SandboxService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.local_worker_path = Path(__file__).resolve().with_name("local_runner_worker.py")

    def extract_entrypoint(self, starter_code: str) -> str:
        try:
            tree = ast.parse(starter_code)
        except SyntaxError:
            return "solve"
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node.name
        return "solve"

    def create_non_executed_result(
        self,
        run_status: str,
        message: str,
        total_count: int,
    ) -> SandboxExecutionResult:
        return SandboxExecutionResult(
            run_status=run_status,
            passed_count=0,
            total_count=total_count,
            score=0.0,
            stdout_excerpt=None,
            stderr_excerpt=message,
            failure_summary=[{"message": message}],
            case_results=[],
            execution_time_ms=None,
        )

    def execute(self, problem: Problem, code: str, test_cases: list[TestCase]) -> SandboxExecutionResult:
        entrypoint = self.extract_entrypoint(problem.starter_code)
        payload = {
            "entrypoint": entrypoint,
            "code": code,
            "tests": [
                {
                    "id": test_case.id,
                    "input_data": test_case.input_data,
                    "expected_output": test_case.expected_output,
                    "is_hidden": test_case.is_hidden,
                }
                for test_case in sorted(test_cases, key=lambda item: item.order_index)
            ],
            "timeout_seconds": self.settings.sandbox_timeout_seconds,
            "memory_limit_mb": self.settings.sandbox_memory_limit_mb,
            "output_limit_bytes": self.settings.sandbox_output_limit_bytes,
            "pids_limit": self.settings.sandbox_pids_limit,
        }
        if self.settings.sandbox_mode in {"remote", "docker"}:
            return self._run_remote(payload, len(test_cases))
        return self._run_local(payload, len(test_cases))

    def _subprocess_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "PYTHONUTF8": "1",
                "PYTHONIOENCODING": "utf-8",
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
            }
        )
        return env

    def _run_local(self, payload: dict[str, Any], total_count: int) -> SandboxExecutionResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            payload_path = temp_path / "payload.json"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            started_at = time.perf_counter()
            try:
                process = subprocess.run(
                    [sys.executable, "-I", "-S", str(self.local_worker_path), str(payload_path)],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.settings.sandbox_timeout_seconds + 1,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    env=self._subprocess_env(),
                )
            except subprocess.TimeoutExpired:
                return self.create_non_executed_result("timeout", "실행 시간이 제한을 초과했습니다.", total_count)
            execution_time_ms = int((time.perf_counter() - started_at) * 1000)
            return self._parse_worker_payload(process.stdout, process.stderr, execution_time_ms, total_count)

    def _run_remote(self, payload: dict[str, Any], total_count: int) -> SandboxExecutionResult:
        started_at = time.perf_counter()
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            **build_runner_headers(self.settings.sandbox_runner_shared_secret, "POST", "/execute", body),
        }
        request = urllib.request.Request(
            url=f"{self.settings.sandbox_runner_url.rstrip('/')}/execute",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.sandbox_timeout_seconds + 1) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                logger.warning("Runner rejected sandbox request with 403.")
                return self.create_non_executed_result("blocked", "샌드박스 실행 요청 인증이 거부되었습니다.", total_count)
            if exc.code == 413:
                logger.warning("Runner rejected sandbox request with 413.")
                return self.create_non_executed_result("blocked", "샌드박스 실행 요청 크기가 제한을 초과했습니다.", total_count)
            logger.exception("Runner returned unexpected HTTP error status=%s", exc.code)
            return self.create_non_executed_result("runtime_error", "샌드박스 서비스 호출에 실패했습니다.", total_count)
        except urllib.error.URLError:
            logger.exception("Runner service is unreachable.")
            return self.create_non_executed_result("runtime_error", "샌드박스 서비스에 연결할 수 없습니다.", total_count)
        execution_time_ms = int((time.perf_counter() - started_at) * 1000)
        data["execution_time_ms"] = execution_time_ms
        return SandboxExecutionResult(**data)

    def _parse_worker_payload(
        self,
        stdout: str,
        stderr: str,
        execution_time_ms: int,
        total_count: int,
    ) -> SandboxExecutionResult:
        limited_stdout = stdout[: self.settings.sandbox_output_limit_bytes]
        limited_stderr = stderr[: self.settings.sandbox_output_limit_bytes]
        try:
            payload = json.loads(limited_stdout)
        except json.JSONDecodeError:
            message = limited_stderr or "샌드박스 실행 결과를 해석하지 못했습니다."
            return self.create_non_executed_result("runtime_error", message, total_count)

        load_error = payload.get("load_error")
        case_results = list(payload.get("results", []))
        if load_error:
            return SandboxExecutionResult(
                run_status="runtime_error",
                passed_count=0,
                total_count=total_count,
                score=0.0,
                stdout_excerpt=(payload.get("module_stdout") or "")[: self.settings.sandbox_output_limit_bytes] or None,
                stderr_excerpt=str(load_error),
                failure_summary=[{"message": str(load_error)}],
                case_results=case_results,
                execution_time_ms=execution_time_ms,
            )

        passed_count = sum(1 for item in case_results if item.get("passed"))
        failure_summary: list[dict[str, Any]] = []
        for item in case_results:
            if item.get("passed"):
                continue
            if item.get("is_hidden"):
                failure_summary.append(
                    {
                        "test_case_id": item.get("id"),
                        "is_hidden": True,
                        "message": "숨겨진 테스트에서 실패했습니다.",
                    }
                )
            else:
                failure_summary.append(
                    {
                        "test_case_id": item.get("id"),
                        "is_hidden": False,
                        "input_data": item.get("input_data"),
                        "expected_output": item.get("expected_output"),
                        "actual_output": item.get("actual_output"),
                        "error": item.get("error"),
                    }
                )
        module_stdout = (payload.get("module_stdout") or "")[: self.settings.sandbox_output_limit_bytes]
        return SandboxExecutionResult(
            run_status="passed" if passed_count == total_count else "failed",
            passed_count=passed_count,
            total_count=total_count,
            score=round(passed_count / total_count, 4) if total_count else 0.0,
            stdout_excerpt=module_stdout or None,
            stderr_excerpt=limited_stderr or None,
            failure_summary=failure_summary,
            case_results=case_results,
            execution_time_ms=execution_time_ms,
        )

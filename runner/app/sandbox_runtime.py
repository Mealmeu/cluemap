from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


class SandboxRuntime:
    def __init__(self, worker_path: Path) -> None:
        self.worker_path = worker_path

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

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        total_count = len(payload["tests"])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            payload_path = temp_path / "payload.json"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            started_at = time.perf_counter()
            try:
                process = subprocess.run(
                    [sys.executable, "-I", "-S", str(self.worker_path), str(payload_path)],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=int(payload["timeout_seconds"]) + 1,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    env=self._subprocess_env(),
                )
            except subprocess.TimeoutExpired:
                return {
                    "run_status": "timeout",
                    "passed_count": 0,
                    "total_count": total_count,
                    "score": 0.0,
                    "stdout_excerpt": None,
                    "stderr_excerpt": "실행 시간이 제한을 초과했습니다.",
                    "failure_summary": [{"message": "실행 시간이 제한을 초과했습니다."}],
                    "case_results": [],
                    "execution_time_ms": None,
                }
            execution_time_ms = int((time.perf_counter() - started_at) * 1000)
            return self._parse_worker_payload(
                process.stdout,
                process.stderr,
                execution_time_ms,
                int(payload["output_limit_bytes"]),
                total_count,
            )

    def _parse_worker_payload(
        self,
        stdout: str,
        stderr: str,
        execution_time_ms: int,
        output_limit_bytes: int,
        total_count: int,
    ) -> dict[str, Any]:
        limited_stdout = stdout[:output_limit_bytes]
        limited_stderr = stderr[:output_limit_bytes]
        try:
            payload = json.loads(limited_stdout)
        except json.JSONDecodeError:
            message = limited_stderr or "샌드박스 실행 결과를 해석하지 못했습니다."
            return {
                "run_status": "runtime_error",
                "passed_count": 0,
                "total_count": total_count,
                "score": 0.0,
                "stdout_excerpt": None,
                "stderr_excerpt": message,
                "failure_summary": [{"message": message}],
                "case_results": [],
                "execution_time_ms": execution_time_ms,
            }

        load_error = payload.get("load_error")
        case_results = list(payload.get("results", []))
        if load_error:
            return {
                "run_status": "runtime_error",
                "passed_count": 0,
                "total_count": total_count,
                "score": 0.0,
                "stdout_excerpt": (payload.get("module_stdout") or "")[:output_limit_bytes] or None,
                "stderr_excerpt": str(load_error),
                "failure_summary": [{"message": str(load_error)}],
                "case_results": case_results,
                "execution_time_ms": execution_time_ms,
            }

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
        return {
            "run_status": "passed" if passed_count == total_count else "failed",
            "passed_count": passed_count,
            "total_count": total_count,
            "score": round(passed_count / total_count, 4) if total_count else 0.0,
            "stdout_excerpt": (payload.get("module_stdout") or "")[:output_limit_bytes] or None,
            "stderr_excerpt": limited_stderr or None,
            "failure_summary": failure_summary,
            "case_results": case_results,
            "execution_time_ms": execution_time_ms,
        }

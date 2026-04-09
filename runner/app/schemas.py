from typing import Any, Optional

from pydantic import BaseModel


class RunnerTestCase(BaseModel):
    id: int
    input_data: dict[str, Any]
    expected_output: Any
    is_hidden: bool


class ExecuteRequest(BaseModel):
    entrypoint: str
    code: str
    tests: list[RunnerTestCase]
    timeout_seconds: int
    memory_limit_mb: int
    output_limit_bytes: int
    pids_limit: int


class ExecuteResponse(BaseModel):
    run_status: str
    passed_count: int
    total_count: int
    score: float
    stdout_excerpt: Optional[str]
    stderr_excerpt: Optional[str]
    failure_summary: list[dict[str, Any]]
    case_results: list[dict[str, Any]]
    execution_time_ms: Optional[int]

from __future__ import annotations

import ast
import contextlib
import io
import json
import sys
from pathlib import Path

try:
    import resource
except ImportError:
    resource = None

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "Exception": Exception,
    "TypeError": TypeError,
    "ValueError": ValueError,
    "IndexError": IndexError,
}
BANNED_CALLS = {
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "memoryview",
    "open",
    "setattr",
    "super",
    "vars",
}
BANNED_NODE_TYPES = (
    ast.Import,
    ast.ImportFrom,
    ast.AsyncFunctionDef,
    ast.AsyncFor,
    ast.AsyncWith,
    ast.Await,
    ast.ClassDef,
    ast.Delete,
    ast.Global,
    ast.Lambda,
    ast.Nonlocal,
    ast.Raise,
    ast.Try,
    ast.With,
    ast.Yield,
    ast.YieldFrom,
)


class LimitedBuffer(io.TextIOBase):
    def __init__(self, byte_limit: int) -> None:
        self.byte_limit = max(byte_limit, 1)
        self.byte_count = 0
        self.parts: list[str] = []

    def write(self, value: str) -> int:
        text = str(value)
        encoded = text.encode("utf-8", errors="ignore")
        remaining = self.byte_limit - self.byte_count
        if remaining <= 0:
            return len(text)
        if len(encoded) > remaining:
            encoded = encoded[:remaining]
            text = encoded.decode("utf-8", errors="ignore")
        self.parts.append(text)
        self.byte_count += len(encoded)
        return len(text)

    def flush(self) -> None:
        return None

    def getvalue(self) -> str:
        return "".join(self.parts)


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def normalize(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [normalize(item) for item in value]
    return repr(value)


def validate_code(code: str):
    tree = ast.parse(code)
    if sum(1 for _ in ast.walk(tree)) > 5000:
        raise ValueError("코드 구조가 너무 복잡합니다.")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("import 문은 허용되지 않습니다.")
        if isinstance(node, BANNED_NODE_TYPES):
            raise ValueError("현재 문제 범위에서 허용되지 않는 문법이 포함되어 있습니다.")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            raise ValueError(f"{node.func.id} 호출은 허용되지 않습니다.")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            if any(keyword.arg == "file" for keyword in node.keywords):
                raise ValueError("print의 file 인자는 허용되지 않습니다.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError("이중 밑줄 속성 접근은 허용되지 않습니다.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("이중 밑줄 이름은 허용되지 않습니다.")
    return tree


def set_limits(payload: dict[str, object]) -> None:
    sys.setrecursionlimit(300)
    if resource is None:
        return
    memory_limit_bytes = int(payload["memory_limit_mb"]) * 1024 * 1024
    timeout_seconds = int(payload["timeout_seconds"])
    pids_limit = max(int(payload["pids_limit"]), 16)
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (timeout_seconds, timeout_seconds + 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    if hasattr(resource, "RLIMIT_CORE"):
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if hasattr(resource, "RLIMIT_NOFILE"):
        resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    if hasattr(resource, "RLIMIT_NPROC"):
        resource.setrlimit(resource.RLIMIT_NPROC, (pids_limit, pids_limit))


def execute_payload(payload: dict[str, object]) -> dict[str, object]:
    configure_stdio()
    set_limits(payload)
    output_limit = int(payload["output_limit_bytes"])
    code = str(payload["code"])
    tree = validate_code(code)
    sandbox_globals = {"__builtins__": SAFE_BUILTINS, "__name__": "student_code"}
    module_stdout = LimitedBuffer(output_limit)
    results = []
    load_error = None

    try:
        compiled = compile(tree, "student_code.py", "exec")
        with contextlib.redirect_stdout(module_stdout), contextlib.redirect_stderr(module_stdout):
            exec(compiled, sandbox_globals, sandbox_globals)
        fn = sandbox_globals.get(str(payload["entrypoint"]))
        if not callable(fn):
            raise AttributeError(f"'{payload['entrypoint']}' 함수를 찾을 수 없습니다.")
    except Exception as exc:
        load_error = f"{type(exc).__name__}: {exc}"
    else:
        for item in payload["tests"]:
            case_stdout = LimitedBuffer(output_limit)
            args = item.get("input_data", {}).get("args", [])
            kwargs = item.get("input_data", {}).get("kwargs", {})
            try:
                with contextlib.redirect_stdout(case_stdout), contextlib.redirect_stderr(case_stdout):
                    actual = fn(*args, **kwargs)
                results.append(
                    {
                        "id": item["id"],
                        "is_hidden": item["is_hidden"],
                        "passed": actual == item.get("expected_output"),
                        "input_data": item.get("input_data", {}),
                        "expected_output": normalize(item.get("expected_output")),
                        "actual_output": normalize(actual),
                        "stdout": case_stdout.getvalue(),
                        "error": None,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "id": item["id"],
                        "is_hidden": item["is_hidden"],
                        "passed": False,
                        "input_data": item.get("input_data", {}),
                        "expected_output": normalize(item.get("expected_output")),
                        "actual_output": None,
                        "stdout": case_stdout.getvalue(),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

    return {
        "load_error": load_error,
        "module_stdout": module_stdout.getvalue(),
        "results": results,
    }


def main() -> None:
    configure_stdio()
    payload_path = Path(sys.argv[1])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    print(json.dumps(execute_payload(payload), ensure_ascii=False))


if __name__ == "__main__":
    main()

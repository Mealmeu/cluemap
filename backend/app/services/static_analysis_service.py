from __future__ import annotations

import ast
from typing import Any


class StaticAnalysisService:
    banned_import_roots = {
        "asyncio",
        "builtins",
        "concurrent",
        "ctypes",
        "http",
        "importlib",
        "inspect",
        "io",
        "marshal",
        "multiprocessing",
        "os",
        "pathlib",
        "pickle",
        "requests",
        "shutil",
        "signal",
        "site",
        "socket",
        "subprocess",
        "sys",
        "tempfile",
        "threading",
        "types",
        "urllib",
    }
    banned_calls = {
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
        "open",
        "setattr",
        "vars",
    }

    def analyze(self, code: str) -> dict[str, Any]:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {
                "syntax_error": True,
                "syntax_message": exc.msg,
                "syntax_line": exc.lineno,
                "function_names": [],
                "has_for": False,
                "has_if": False,
                "has_return": False,
                "has_accumulator": False,
                "has_sum_call": False,
                "has_max_call": False,
                "banned_imports": [],
                "dangerous_calls": [],
                "dunder_access": False,
            }

        function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        banned_imports: list[str] = []
        dangerous_calls: list[str] = []
        has_accumulator = False
        has_sum_call = False
        has_max_call = False
        dunder_access = False

        for node in ast.walk(tree):
            if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                has_accumulator = True
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"total", "count", "result", "answer", "max_value", "current_max"}:
                        has_accumulator = True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "sum":
                    has_sum_call = True
                if node.func.id == "max":
                    has_max_call = True
                if node.func.id in self.banned_calls:
                    dangerous_calls.append(node.func.id)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in self.banned_import_roots:
                        banned_imports.append(alias.name)
            if isinstance(node, ast.ImportFrom):
                module = (node.module or "").split(".")[0]
                if module in self.banned_import_roots:
                    banned_imports.append(node.module or "")
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                dunder_access = True
            if isinstance(node, ast.Name) and node.id.startswith("__"):
                dunder_access = True

        return {
            "syntax_error": False,
            "syntax_message": None,
            "syntax_line": None,
            "function_names": function_names,
            "has_for": any(isinstance(node, ast.For) for node in ast.walk(tree)),
            "has_if": any(isinstance(node, ast.If) for node in ast.walk(tree)),
            "has_return": any(isinstance(node, ast.Return) for node in ast.walk(tree)),
            "has_accumulator": has_accumulator,
            "has_sum_call": has_sum_call,
            "has_max_call": has_max_call,
            "banned_imports": sorted(set(banned_imports)),
            "dangerous_calls": sorted(set(dangerous_calls)),
            "dunder_access": dunder_access,
        }

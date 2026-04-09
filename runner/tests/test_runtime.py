from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.sandbox_runtime import SandboxRuntime


class RunnerRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = SandboxRuntime(ROOT / "app" / "worker.py")

    def test_hidden_failure_message_is_korean(self) -> None:
        payload = {
            "entrypoint": "solve",
            "code": "def solve(numbers):\n    return 999\n",
            "tests": [
                {
                    "id": 1,
                    "input_data": {"args": [[1, 2, 3, 4]]},
                    "expected_output": 6,
                    "is_hidden": True,
                }
            ],
            "timeout_seconds": 1,
            "memory_limit_mb": 64,
            "output_limit_bytes": 4096,
            "pids_limit": 32,
        }
        result = self.runtime.execute(payload)
        self.assertEqual(result["run_status"], "failed")
        self.assertEqual(result["failure_summary"][0]["message"], "숨겨진 테스트에서 실패했습니다.")

    def test_blocked_import_message_is_korean(self) -> None:
        payload = {
            "entrypoint": "solve",
            "code": "import os\ndef solve(numbers):\n    return 0\n",
            "tests": [
                {
                    "id": 1,
                    "input_data": {"args": [[1, 2, 3, 4]]},
                    "expected_output": 6,
                    "is_hidden": False,
                }
            ],
            "timeout_seconds": 1,
            "memory_limit_mb": 64,
            "output_limit_bytes": 4096,
            "pids_limit": 32,
        }
        result = self.runtime.execute(payload)
        self.assertEqual(result["run_status"], "runtime_error")
        self.assertIn("import 문은 허용되지 않습니다.", result["stderr_excerpt"])


if __name__ == "__main__":
    unittest.main()
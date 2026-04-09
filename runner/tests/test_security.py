from __future__ import annotations

import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.security import NonceStore, build_runner_signature, verify_runner_request


class RunnerSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.secret = "runner-secret-1234567890"
        self.body = json.dumps({"value": 1}, ensure_ascii=False).encode("utf-8")

    def test_valid_signature_and_replay_block(self) -> None:
        timestamp = str(int(time.time()))
        nonce = "nonce-1234567890-abcdef"
        signature = build_runner_signature(self.secret, "POST", "/execute", timestamp, nonce, self.body)
        store = NonceStore(60)

        verify_runner_request(self.secret, "POST", "/execute", self.body, timestamp, nonce, signature, 30, store)

        with self.assertRaisesRegex(ValueError, "이미 처리된 실행 요청입니다."):
            verify_runner_request(self.secret, "POST", "/execute", self.body, timestamp, nonce, signature, 30, store)

    def test_invalid_signature_is_rejected(self) -> None:
        timestamp = str(int(time.time()))
        nonce = "nonce-1234567890-ghijkl"
        store = NonceStore(60)

        with self.assertRaisesRegex(ValueError, "실행 요청 서명이 올바르지 않습니다."):
            verify_runner_request(self.secret, "POST", "/execute", self.body, timestamp, nonce, "bad-signature", 30, store)

    def test_expired_timestamp_is_rejected(self) -> None:
        timestamp = str(int(time.time()) - 120)
        nonce = "nonce-1234567890-expired"
        signature = build_runner_signature(self.secret, "POST", "/execute", timestamp, nonce, self.body)
        store = NonceStore(300)

        with self.assertRaisesRegex(ValueError, "실행 요청 서명 유효 시간이 지났습니다."):
            verify_runner_request(self.secret, "POST", "/execute", self.body, timestamp, nonce, signature, 30, store)

    def test_malformed_nonce_and_signature_are_rejected(self) -> None:
        timestamp = str(int(time.time()))
        store = NonceStore(60)

        with self.assertRaisesRegex(ValueError, "실행 요청 nonce 형식이 올바르지 않습니다."):
            verify_runner_request(self.secret, "POST", "/execute", self.body, timestamp, "bad nonce", "a" * 64, 30, store)

        with self.assertRaisesRegex(ValueError, "실행 요청 서명이 올바르지 않습니다."):
            verify_runner_request(
                self.secret,
                "POST",
                "/execute",
                self.body,
                timestamp,
                "nonce-1234567890-format",
                "not-hex-signature",
                30,
                store,
            )


if __name__ == "__main__":
    unittest.main()

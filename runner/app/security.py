from __future__ import annotations

import hashlib
import hmac
import re
import time
from threading import Lock

RUNNER_TIMESTAMP_HEADER = "X-Runner-Timestamp"
RUNNER_NONCE_HEADER = "X-Runner-Nonce"
RUNNER_SIGNATURE_HEADER = "X-Runner-Signature"
NONCE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
SIGNATURE_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class NonceStore:
    def __init__(self, ttl_seconds: int, max_entries: int = 4096) -> None:
        self.ttl_seconds = max(ttl_seconds, 1)
        self.max_entries = max_entries
        self.values: dict[str, float] = {}
        self.lock = Lock()

    def _cleanup(self, now: float) -> None:
        expired = [nonce for nonce, expires_at in self.values.items() if expires_at <= now]
        for nonce in expired:
            self.values.pop(nonce, None)
        if len(self.values) > self.max_entries:
            oldest = sorted(self.values.items(), key=lambda item: item[1])[: len(self.values) - self.max_entries]
            for nonce, _ in oldest:
                self.values.pop(nonce, None)

    def mark(self, nonce: str, now: float) -> bool:
        with self.lock:
            self._cleanup(now)
            expires_at = self.values.get(nonce)
            if expires_at and expires_at > now:
                return False
            self.values[nonce] = now + self.ttl_seconds
            return True


def build_runner_signature(
    secret: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = "\n".join([method.upper(), path, timestamp, nonce, body_hash]).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()


def verify_runner_request(
    secret: str,
    method: str,
    path: str,
    body: bytes,
    timestamp: str | None,
    nonce: str | None,
    signature: str | None,
    ttl_seconds: int,
    nonce_store: NonceStore,
) -> None:
    if not timestamp or not nonce or not signature:
        raise ValueError("실행 요청 인증 헤더가 누락되었습니다.")
    if not NONCE_PATTERN.fullmatch(nonce):
        raise ValueError("실행 요청 nonce 형식이 올바르지 않습니다.")
    if not timestamp.isdigit() or len(timestamp) < 10 or len(timestamp) > 12:
        raise ValueError("실행 요청 시각 형식이 올바르지 않습니다.")
    if not SIGNATURE_PATTERN.fullmatch(signature):
        raise ValueError("실행 요청 서명이 올바르지 않습니다.")
    try:
        issued_at = int(timestamp)
    except ValueError as exc:
        raise ValueError("실행 요청 시각 형식이 올바르지 않습니다.") from exc
    now = int(time.time())
    if abs(now - issued_at) > ttl_seconds:
        raise ValueError("실행 요청 서명 유효 시간이 지났습니다.")
    expected_signature = build_runner_signature(secret, method, path, timestamp, nonce, body)
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("실행 요청 서명이 올바르지 않습니다.")
    if not nonce_store.mark(nonce, float(now)):
        raise ValueError("이미 처리된 실행 요청입니다.")

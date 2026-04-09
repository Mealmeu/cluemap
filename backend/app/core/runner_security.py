from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Dict

RUNNER_TIMESTAMP_HEADER = "X-Runner-Timestamp"
RUNNER_NONCE_HEADER = "X-Runner-Nonce"
RUNNER_SIGNATURE_HEADER = "X-Runner-Signature"


def build_runner_signature(
    secret: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    body_hash = hashlib.sha256(body).hexdigest()
    canonical = "\n".join(
        [
            method.upper(),
            path,
            timestamp,
            nonce,
            body_hash,
        ]
    ).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()


def build_runner_headers(secret: str, method: str, path: str, body: bytes) -> Dict[str, str]:
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(24)
    signature = build_runner_signature(secret, method, path, timestamp, nonce, body)
    return {
        RUNNER_TIMESTAMP_HEADER: timestamp,
        RUNNER_NONCE_HEADER: nonce,
        RUNNER_SIGNATURE_HEADER: signature,
    }

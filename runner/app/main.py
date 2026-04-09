from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request, status
from pydantic import ValidationError

from app.sandbox_runtime import SandboxRuntime
from app.schemas import ExecuteRequest, ExecuteResponse
from app.security import NonceStore, verify_runner_request
from app.settings import get_settings

settings = get_settings()
runtime = SandboxRuntime(Path(__file__).resolve().parent / "worker.py")
nonce_store = NonceStore(settings.sandbox_runner_nonce_cache_seconds)
logger = logging.getLogger(__name__)
app = FastAPI(title="ClueMap Runner", docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/execute", response_model=ExecuteResponse)
async def execute(
    request: Request,
    x_runner_timestamp: Optional[str] = Header(default=None),
    x_runner_nonce: Optional[str] = Header(default=None),
    x_runner_signature: Optional[str] = Header(default=None),
) -> ExecuteResponse:
    body = await request.body()
    if len(body) > settings.sandbox_runner_max_request_body_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="실행 요청 크기가 제한을 초과했습니다.")
    try:
        verify_runner_request(
            secret=settings.sandbox_runner_shared_secret,
            method=request.method,
            path=request.url.path,
            body=body,
            timestamp=x_runner_timestamp,
            nonce=x_runner_nonce,
            signature=x_runner_signature,
            ttl_seconds=settings.sandbox_runner_signature_ttl_seconds,
            nonce_store=nonce_store,
        )
    except ValueError as exc:
        client_ip = request.client.host if request.client else "unknown"
        logger.warning("Runner request rejected ip=%s path=%s reason=%s", client_ip, request.url.path, exc)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="실행 요청 인증이 거부되었습니다.") from exc
    try:
        payload = ExecuteRequest.model_validate_json(body)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="실행 요청 형식이 올바르지 않습니다.") from exc
    result = runtime.execute(payload.model_dump())
    return ExecuteResponse.model_validate(result)

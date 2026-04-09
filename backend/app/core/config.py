from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ClueMap API"
    api_prefix: str = "/api"
    environment: str = "development"
    debug: bool = False
    database_url: str = "sqlite:///./cluemap.db"
    frontend_origin: str = "http://localhost:5173"
    cors_origins_raw: str = "http://localhost:5173,http://localhost:4173"
    trusted_hosts_raw: str = "localhost,127.0.0.1,testserver"
    csrf_trusted_origins_raw: str = "http://localhost,http://127.0.0.1,http://localhost:5173,http://localhost:4173"
    access_token_secret: str = "change-me-access-secret"
    refresh_token_secret: str = "change-me-refresh-secret"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 14
    refresh_cookie_name: str = "cluemap_refresh_token"
    refresh_cookie_path: str = "/api/auth"
    csrf_cookie_name: str = "cluemap_csrf_token"
    csrf_cookie_path: str = "/"
    csrf_header_name: str = "X-CSRF-Token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    csrf_cookie_samesite: str = "strict"
    cookie_domain: Optional[str] = None
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 300
    allow_refresh_token_in_body: bool = False
    max_request_body_bytes: int = 65536
    sandbox_mode: str = "local"
    sandbox_runner_image: str = "cluemap-python-runner:latest"
    sandbox_runner_url: str = "http://runner:9000"
    sandbox_runner_shared_secret: str = "change-me-runner-secret"
    sandbox_runner_signature_ttl_seconds: int = 30
    sandbox_timeout_seconds: int = 3
    sandbox_memory_limit_mb: int = 128
    sandbox_output_limit_bytes: int = 16384
    sandbox_pids_limit: int = 64
    max_submission_code_size: int = 20000
    llm_provider: str = "local"
    llm_timeout_seconds: int = 20
    local_llm_profile_name: str = "ClueMap KR Analyzer"
    local_llm_model_repo: str = "Qwen/Qwen3-4B-Instruct-2507"
    local_llm_model_file: str = "cluemap-kr-analyzer-qwen3-4b-q4_k_m.gguf"
    local_llm_download_repo: str = "bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF"
    local_llm_download_file: str = "Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
    local_llm_model_dir: str = "/models"
    local_llm_auto_download: bool = False
    local_llm_chat_format: str = "chatml"
    local_llm_n_ctx: int = 2048
    local_llm_n_threads: int = 4
    local_llm_n_gpu_layers: int = 0
    local_llm_temperature: float = 0.2
    local_llm_top_p: float = 0.9
    local_llm_top_k: int = 40
    local_llm_repeat_penalty: float = 1.08
    local_llm_max_tokens: int = 384
    local_llm_seed: int = 42
    analysis_version: str = "2026.04.cluemap-kr-analyzer-v2"
    teacher_focus_topic_limit: int = 3
    hidden_failure_preview_limit: int = 2

    @staticmethod
    def _parse_csv(raw_value: str) -> List[str]:
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @staticmethod
    def _extract_host(value: str) -> Optional[str]:
        parsed = urlparse(value)
        return parsed.hostname

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        origins = self._parse_csv(self.cors_origins_raw)
        if self.frontend_origin not in origins:
            origins.append(self.frontend_origin)
        return origins

    @property
    def trusted_hosts(self) -> List[str]:
        hosts = self._parse_csv(self.trusted_hosts_raw)
        extracted_hosts = [
            self._extract_host(self.frontend_origin),
            *[self._extract_host(origin) for origin in self.cors_origins],
        ]
        for host in extracted_hosts:
            if host and host not in hosts:
                hosts.append(host)
        return hosts

    @property
    def csrf_trusted_origins(self) -> List[str]:
        origins = self._parse_csv(self.csrf_trusted_origins_raw)
        if self.frontend_origin not in origins:
            origins.append(self.frontend_origin)
        return origins

    @property
    def local_llm_model_path(self) -> str:
        return str(Path(self.local_llm_model_dir) / self.local_llm_model_file)

    @model_validator(mode="after")
    def validate_security_configuration(self) -> "Settings":
        cookie_samesite = self.cookie_samesite.lower()
        csrf_cookie_samesite = self.csrf_cookie_samesite.lower()
        allowed_cookie_modes = {"lax", "strict", "none"}

        if cookie_samesite not in allowed_cookie_modes:
            raise ValueError("COOKIE_SAMESITE must be one of lax, strict, none.")
        if csrf_cookie_samesite not in allowed_cookie_modes:
            raise ValueError("CSRF_COOKIE_SAMESITE must be one of lax, strict, none.")
        if cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true when COOKIE_SAMESITE is none.")
        if csrf_cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true when CSRF_COOKIE_SAMESITE is none.")
        if self.max_request_body_bytes < self.max_submission_code_size:
            raise ValueError("MAX_REQUEST_BODY_BYTES must be greater than or equal to MAX_SUBMISSION_CODE_SIZE.")
        if self.sandbox_mode == "remote" and not self.sandbox_runner_url:
            raise ValueError("SANDBOX_RUNNER_URL is required when SANDBOX_MODE is remote.")
        if self.sandbox_runner_signature_ttl_seconds < 5:
            raise ValueError("SANDBOX_RUNNER_SIGNATURE_TTL_SECONDS must be at least 5.")
        if self.sandbox_runner_signature_ttl_seconds > self.refresh_token_ttl_days * 24 * 60 * 60:
            raise ValueError("SANDBOX_RUNNER_SIGNATURE_TTL_SECONDS is unexpectedly high.")
        if self.local_llm_top_k < 1:
            raise ValueError("LOCAL_LLM_TOP_K must be greater than 0.")
        if self.local_llm_repeat_penalty < 1.0:
            raise ValueError("LOCAL_LLM_REPEAT_PENALTY must be greater than or equal to 1.0.")

        if self.is_production:
            insecure_values = {
                "change-me-access-secret",
                "change-me-refresh-secret",
                "change-me-runner-secret",
            }
            if self.access_token_secret in insecure_values or len(self.access_token_secret) < 32:
                raise ValueError("ACCESS_TOKEN_SECRET must be replaced with a strong production secret.")
            if self.refresh_token_secret in insecure_values or len(self.refresh_token_secret) < 32:
                raise ValueError("REFRESH_TOKEN_SECRET must be replaced with a strong production secret.")
            if self.sandbox_runner_shared_secret in insecure_values or len(self.sandbox_runner_shared_secret) < 32:
                raise ValueError("SANDBOX_RUNNER_SHARED_SECRET must be replaced with a strong production secret.")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true in production.")
            if not self.frontend_origin.startswith("https://"):
                raise ValueError("FRONTEND_ORIGIN must use https in production.")
            if self.allow_refresh_token_in_body:
                raise ValueError("ALLOW_REFRESH_TOKEN_IN_BODY must be false in production.")
            if "*" in self.trusted_hosts:
                raise ValueError("TRUSTED_HOSTS_RAW cannot contain * in production.")
            if any(not origin.startswith("https://") for origin in self.cors_origins):
                raise ValueError("All CORS origins must use https in production.")
            if any(not origin.startswith("https://") for origin in self.csrf_trusted_origins):
                raise ValueError("All CSRF trusted origins must use https in production.")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

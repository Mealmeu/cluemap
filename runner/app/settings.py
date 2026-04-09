from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    sandbox_runner_shared_secret: str = "change-me-runner-secret"
    sandbox_runner_signature_ttl_seconds: int = 30
    sandbox_runner_nonce_cache_seconds: int = 300
    sandbox_runner_max_request_body_bytes: int = 65536
    sandbox_timeout_seconds: int = 3
    sandbox_memory_limit_mb: int = 128
    sandbox_output_limit_bytes: int = 16384
    sandbox_pids_limit: int = 64

    @model_validator(mode="after")
    def validate_security_configuration(self) -> "Settings":
        if self.sandbox_runner_signature_ttl_seconds < 5:
            raise ValueError("SANDBOX_RUNNER_SIGNATURE_TTL_SECONDS must be at least 5.")
        if self.sandbox_runner_nonce_cache_seconds < self.sandbox_runner_signature_ttl_seconds:
            raise ValueError("SANDBOX_RUNNER_NONCE_CACHE_SECONDS must be greater than or equal to SANDBOX_RUNNER_SIGNATURE_TTL_SECONDS.")
        if self.sandbox_runner_max_request_body_bytes < 1024:
            raise ValueError("SANDBOX_RUNNER_MAX_REQUEST_BODY_BYTES must be at least 1024.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

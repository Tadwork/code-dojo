"""Application configuration."""

import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/coddojo"

    # Application
    environment: str = "development"
    port: int = 8000
    secret_key: str = "dev-secret-key-change-in-production"
    e2b_api_key: str = ""
    execution_timeout_seconds: float = 10
    execution_request_timeout_seconds: float = 15

    # CORS
    cors_origins: list[str] = DEFAULT_CORS_ORIGINS.copy()

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @field_validator("database_url", mode="after")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Convert PostgreSQL URLs to asyncpg form."""
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """Accept comma-separated origin lists from environment variables."""
        if value in (None, ""):
            return DEFAULT_CORS_ORIGINS.copy()
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        raise ValueError("Invalid CORS_ORIGINS value")

    def get_cors_origins(self) -> list[str]:
        """Get CORS origins, adding the Render URL if in production."""
        origins = self.cors_origins.copy()
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url and render_url not in origins:
            origins.append(render_url)
        return origins

settings = Settings()

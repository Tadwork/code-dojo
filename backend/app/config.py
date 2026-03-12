"""Application configuration."""

import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/coddojo"
    )

    def __init__(self, **data):
        """Initialize settings and convert PostgreSQL URLs to use asyncpg."""
        super().__init__(**data)
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )

    # Application
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", "8000"))
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    e2b_api_key: str = os.getenv("E2B_API_KEY", "")
    execution_timeout_seconds: float = float(os.getenv("EXECUTION_TIMEOUT_SECONDS", "10"))
    execution_request_timeout_seconds: float = float(
        os.getenv("EXECUTION_REQUEST_TIMEOUT_SECONDS", "15")
    )

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    def get_cors_origins(self) -> list[str]:
        """Get CORS origins, adding the Render URL if in production."""
        origins = self.cors_origins.copy()
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url and render_url not in origins:
            origins.append(render_url)
        return origins

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()

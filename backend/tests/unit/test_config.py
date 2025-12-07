"""Unit tests for configuration module."""

from app.config import Settings, settings


class TestSettings:
    """Test Settings class."""

    def test_default_database_url(self):
        """Test default database URL."""
        test_settings = Settings()
        assert "postgresql+asyncpg://" in test_settings.database_url

    def test_default_environment(self):
        """Test default environment."""
        test_settings = Settings()
        assert test_settings.environment == "development"

    def test_default_port(self):
        """Test default port."""
        test_settings = Settings()
        assert test_settings.port == 8000

    def test_default_secret_key(self):
        """Test default secret key."""
        test_settings = Settings()
        assert test_settings.secret_key == "dev-secret-key-change-in-production"

    def test_default_cors_origins(self):
        """Test default CORS origins."""
        test_settings = Settings()
        assert "http://localhost:3000" in test_settings.cors_origins
        assert "http://localhost:8000" in test_settings.cors_origins

    def test_environment_variable_override(self, monkeypatch):
        """Test environment variable override."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key")

        test_settings = Settings()
        assert test_settings.environment == "production"
        assert test_settings.port == 9000
        assert test_settings.secret_key == "test-secret-key"

    def test_settings_singleton(self):
        """Test that settings is a singleton instance."""
        assert settings is not None
        assert isinstance(settings, Settings)

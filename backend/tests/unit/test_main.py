"""Unit tests for main application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestMainApp:
    """Test main FastAPI application."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data

    def test_app_title(self):
        """Test app title is set correctly."""
        assert app.title == "CodeDojo API"

    def test_app_version(self):
        """Test app version is set correctly."""
        assert app.version == "0.1.0"

    def test_routers_included(self):
        """Test that routers are included."""
        routes = [route.path for route in app.routes]
        assert "/api/sessions" in str(routes)
        assert "/ws/{session_code}" in str(routes)


"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAPIIntegration:
    """Integration tests for API."""

    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


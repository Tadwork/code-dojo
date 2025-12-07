"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import main


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

    def test_spa_fallback_serves_index(self, client, tmp_path, monkeypatch):
        """Ensure unknown routes return the React index when available."""
        index_file = tmp_path / "index.html"
        index_file.write_text("<html><body>SPA</body></html>", encoding="utf-8")

        # Point the SPA handler at the temporary build directory
        monkeypatch.setattr(main, "static_dir", tmp_path)

        response = client.get("/session/ABC123")

        assert response.status_code == 200
        assert "SPA" in response.text

"""Tests for AI assistant route."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_success():
    """Test successful code generation."""
    mock_result = {"code": "def hello():\n    print('Hello')", "error": ""}
    
    with patch("app.routes.assistant.generate_code", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_result
        
        response = client.post(
            "/api/assistant/generate",
            json={"prompt": "Create a hello function", "code": "", "language": "python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == mock_result["code"]
        assert data["error"] == ""


def test_generate_empty_prompt():
    """Test that empty prompt returns 400."""
    response = client.post(
        "/api/assistant/generate",
        json={"prompt": "   ", "code": "", "language": "python"}
    )
    
    assert response.status_code == 400
    assert "Prompt is required" in response.json()["detail"]


def test_generate_with_existing_code():
    """Test code modification with existing code."""
    mock_result = {"code": "def hello():\n    # Modified\n    print('Hello')", "error": ""}
    
    with patch("app.routes.assistant.generate_code", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_result
        
        response = client.post(
            "/api/assistant/generate",
            json={
                "prompt": "Add a comment",
                "code": "def hello():\n    print('Hello')",
                "language": "python"
            }
        )
        
        assert response.status_code == 200
        mock_generate.assert_called_once()


def test_generate_with_error_response():
    """Test handling of AI service errors."""
    mock_result = {"code": "", "error": "AI service unavailable"}
    
    with patch("app.routes.assistant.generate_code", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_result
        
        response = client.post(
            "/api/assistant/generate",
            json={"prompt": "Create something", "code": "", "language": "python"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == ""
        assert data["error"] == "AI service unavailable"

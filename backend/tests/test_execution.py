"""Tests for code execution endpoint."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_execute_python_success():
    """Test successful Python execution."""
    mock_result = {"output": "hello\n", "error": ""}

    with patch("app.routes.execution.execute_source", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result

        response = client.post(
            "/api/execute", json={"code": "print('hello')", "language": "python"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["output"].strip() == "hello"
        assert data["error"] == ""


def test_execute_javascript_success():
    """Test successful JavaScript execution."""
    mock_result = {"output": "hello\n", "error": ""}

    with patch("app.routes.execution.execute_source", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result

        response = client.post(
            "/api/execute", json={"code": "console.log('hello')", "language": "javascript"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["output"].strip() == "hello"
        assert data["error"] == ""


def test_execute_unsupported_language():
    """Test that unsupported languages return 400."""
    response = client.post(
        "/api/execute", json={"code": "print('hello')", "language": "brainfuck"}
    )
    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]


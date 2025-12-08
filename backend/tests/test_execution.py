from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_execute_python_success():
    response = client.post("/api/execute", json={"code": "print('hello')", "language": "python"})
    assert response.status_code == 200
    data = response.json()
    assert data["output"].strip() == "hello"
    assert data["error"] == ""


def test_execute_javascript_success():
    response = client.post(
        "/api/execute", json={"code": "console.log('hello')", "language": "javascript"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["output"].strip() == "hello"
    assert data["error"] == ""


def test_execute_unsupported_language():
    response = client.post("/api/execute", json={"code": "print('hello')", "language": "java"})
    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]

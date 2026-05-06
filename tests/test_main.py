from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_root_message():
    response = client.get("/")
    assert response.json()["message"] == "CI/CD + DevSecOps Demo API"


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_status_is_ok():
    response = client.get("/health")
    assert response.json()["status"] == "ok"


def test_version_returns_200():
    response = client.get("/version")
    assert response.status_code == 200


def test_version_value():
    response = client.get("/version")
    assert response.json()["version"] == "1.0.0"

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_health_endpoint_exists(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/api/health")
    assert response.content_type == "application/json"


def test_health_success_is_true(client):
    response = client.get("/api/health")
    data = response.get_json()
    assert data["success"] is True


def test_health_has_message(client):
    response = client.get("/api/health")
    data = response.get_json()
    assert "message" in data

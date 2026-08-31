"""Tests for JWT auth protection on animal/assessment routes and /api/auth/me."""

import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from app import create_app
from app.config import TestingConfig

TEST_USER_ID = 1
TEST_USER_EMAIL = "test@example.com"


def _make_token(user_id=TEST_USER_ID, email=TEST_USER_EMAIL, expired=False, secret=None):
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": now - timedelta(hours=1) if expired else now + timedelta(hours=1),
        "iat": now,
    }
    return jwt.encode(payload, secret or TestingConfig.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


class TestAnimalsRouteProtection:
    def test_no_auth_header_returns_401(self, client):
        resp = client.get("/api/animals")
        assert resp.status_code == 401
        assert resp.get_json()["success"] is False

    def test_malformed_header_returns_401(self, client):
        resp = client.get("/api/animals", headers={"Authorization": "sometoken"})
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get(
            "/api/animals", headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert resp.status_code == 401

    def test_expired_token_returns_401(self, client):
        token = _make_token(expired=True)
        resp = client.get("/api/animals", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_wrong_secret_returns_401(self, client):
        token = _make_token(secret="wrong-secret")
        resp = client.get("/api/animals", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_valid_token_allows_access(self, client):
        token = _make_token()
        resp = client.get("/api/animals", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_post_without_auth_returns_401(self, client):
        resp = client.post(
            "/api/animals",
            data=json.dumps({"name": "Moti", "animal_type": "Cow"}),
            content_type="application/json",
        )
        assert resp.status_code == 401


class TestHealthEndpointStillPublic:
    def test_health_does_not_require_auth(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200


class TestAuthMe:
    def test_me_requires_auth(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_returns_current_user(self, client):
        signup_resp = client.post(
            "/api/auth/signup",
            data=json.dumps(
                {"name": "Tayyab", "email": "me@example.com", "password": "password123"}
            ),
            content_type="application/json",
        )
        token = signup_resp.get_json()["data"]["token"]

        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        assert body["email"] == "me@example.com"
        assert "password_hash" not in body
        assert "password" not in body
"""
Tests for AuthService using a fake in-memory UserRepository —
no real MongoDB connection needed for these tests.
"""

import jwt
import pytest

from app.services.auth_service import (
    AuthenticationError,
    AuthService,
    DuplicateEmailError,
    ValidationError,
)

SECRET_KEY = "test-secret-key"


class FakeUserRepository:
    """Minimal in-memory stand-in for UserRepository, for testing only."""

    def __init__(self):
        self._users = {}
        self._next_id = 1

    def create(self, data):
        user_id = str(self._next_id)
        self._next_id += 1
        record = {"id": user_id, **data}
        self._users[user_id] = record
        self._users_by_email = getattr(self, "_users_by_email", {})
        self._users_by_email[data["email"]] = record
        return dict(record)

    def get_by_email(self, email):
        record = getattr(self, "_users_by_email", {}).get(email)
        return dict(record) if record else None

    def get_by_id(self, user_id):
        record = self._users.get(user_id)
        return dict(record) if record else None


@pytest.fixture
def service():
    return AuthService(repository=FakeUserRepository(), secret_key=SECRET_KEY)


VALID_SIGNUP = {
    "name": "Tayyab",
    "email": "test@example.com",
    "password": "password123",
}


class TestSignup:
    def test_signup_success_returns_user_and_token(self, service):
        result = service.signup(VALID_SIGNUP)
        assert "token" in result
        assert result["user"]["email"] == "test@example.com"
        assert "password_hash" not in result["user"]
        assert "password" not in result["user"]

    def test_signup_token_is_valid_jwt(self, service):
        result = service.signup(VALID_SIGNUP)
        payload = jwt.decode(result["token"], SECRET_KEY, algorithms=["HS256"])
        assert payload["email"] == "test@example.com"

    def test_signup_invalid_data_raises_validation_error(self, service):
        with pytest.raises(ValidationError):
            service.signup({"email": "bad", "password": "123"})

    def test_signup_duplicate_email_raises_error(self, service):
        service.signup(VALID_SIGNUP)
        with pytest.raises(DuplicateEmailError):
            service.signup(VALID_SIGNUP)


class TestLogin:
    def test_login_success_returns_token(self, service):
        service.signup(VALID_SIGNUP)
        result = service.login(
            {"email": "test@example.com", "password": "password123"}
        )
        assert "token" in result
        assert "password_hash" not in result["user"]

    def test_login_wrong_password_raises_auth_error(self, service):
        service.signup(VALID_SIGNUP)
        with pytest.raises(AuthenticationError):
            service.login({"email": "test@example.com", "password": "wrongpass"})

    def test_login_nonexistent_email_raises_auth_error(self, service):
        with pytest.raises(AuthenticationError):
            service.login({"email": "ghost@example.com", "password": "password123"})

    def test_login_invalid_data_raises_validation_error(self, service):
        with pytest.raises(ValidationError):
            service.login({"email": "test@example.com"})
"""Tests for user validation logic (signup and login)."""

import pytest
from app.services.user_validation import validate_login_data, validate_signup_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_signup(**overrides):
    """Return a minimal valid signup payload, with optional overrides."""
    base = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepass123",
    }
    base.update(overrides)
    return base


def _valid_login(**overrides):
    """Return a minimal valid login payload, with optional overrides."""
    base = {
        "email": "test@example.com",
        "password": "securepass123",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Signup validation
# ---------------------------------------------------------------------------

class TestSignupValidation:
    # --- Valid payloads ----------------------------------------------------

    def test_valid_signup_data(self):
        errors = validate_signup_data(_valid_signup())
        assert errors == []

    def test_valid_signup_with_long_password(self):
        errors = validate_signup_data(_valid_signup(password="a" * 50))
        assert errors == []

    # --- Name field --------------------------------------------------------

    def test_missing_name(self):
        data = {"email": "test@example.com", "password": "securepass123"}
        errors = validate_signup_data(data)
        assert any("name" in e for e in errors)

    def test_empty_name(self):
        errors = validate_signup_data(_valid_signup(name=""))
        assert any("name" in e for e in errors)

    def test_whitespace_only_name(self):
        errors = validate_signup_data(_valid_signup(name="   "))
        assert any("name" in e for e in errors)

    def test_null_name(self):
        errors = validate_signup_data(_valid_signup(name=None))
        assert any("name" in e for e in errors)

    def test_name_not_a_string(self):
        errors = validate_signup_data(_valid_signup(name=123))
        assert any("name" in e and "string" in e for e in errors)

    def test_name_too_long(self):
        errors = validate_signup_data(_valid_signup(name="x" * 101))
        assert any("100" in e for e in errors)

    # --- Email field -------------------------------------------------------

    def test_missing_email(self):
        data = {"name": "Test", "password": "securepass123"}
        errors = validate_signup_data(data)
        assert any("email" in e for e in errors)

    def test_empty_email(self):
        errors = validate_signup_data(_valid_signup(email=""))
        assert any("email" in e for e in errors)

    def test_whitespace_only_email(self):
        errors = validate_signup_data(_valid_signup(email="   "))
        assert any("email" in e for e in errors)

    def test_null_email(self):
        errors = validate_signup_data(_valid_signup(email=None))
        assert any("email" in e for e in errors)

    def test_invalid_email_no_at(self):
        errors = validate_signup_data(_valid_signup(email="testexample.com"))
        assert any("valid email" in e for e in errors)

    def test_invalid_email_no_domain(self):
        errors = validate_signup_data(_valid_signup(email="test@"))
        assert any("valid email" in e for e in errors)

    def test_invalid_email_no_tld(self):
        errors = validate_signup_data(_valid_signup(email="test@example"))
        assert any("valid email" in e for e in errors)

    def test_valid_email_formats(self):
        """Should accept various valid email formats."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
        ]
        for email in valid_emails:
            errors = validate_signup_data(_valid_signup(email=email))
            assert errors == [], f"Unexpected errors for '{email}': {errors}"

    def test_email_too_long(self):
        long_email = "a" * 250 + "@b.co"
        errors = validate_signup_data(_valid_signup(email=long_email))
        assert any("254" in e for e in errors)

    # --- Password field ----------------------------------------------------

    def test_missing_password(self):
        data = {"name": "Test", "email": "test@example.com"}
        errors = validate_signup_data(data)
        assert any("password" in e for e in errors)

    def test_empty_password(self):
        errors = validate_signup_data(_valid_signup(password=""))
        assert any("password" in e for e in errors)

    def test_null_password(self):
        errors = validate_signup_data(_valid_signup(password=None))
        assert any("password" in e for e in errors)

    def test_password_too_short(self):
        errors = validate_signup_data(_valid_signup(password="short"))
        assert any("password" in e and "8" in e for e in errors)

    def test_password_exactly_8_chars(self):
        errors = validate_signup_data(_valid_signup(password="12345678"))
        assert errors == []

    def test_password_not_a_string(self):
        errors = validate_signup_data(_valid_signup(password=12345678))
        assert any("password" in e and "string" in e for e in errors)

    # --- Non-dict input ----------------------------------------------------

    def test_non_dict_input(self):
        errors = validate_signup_data([1, 2, 3])
        assert any("JSON object" in e for e in errors)

    # --- Multiple errors ---------------------------------------------------

    def test_multiple_errors_reported(self):
        errors = validate_signup_data({})
        # Should have errors for name, email, and password
        assert len(errors) >= 3


# ---------------------------------------------------------------------------
# Login validation
# ---------------------------------------------------------------------------

class TestLoginValidation:
    # --- Valid payloads ----------------------------------------------------

    def test_valid_login_data(self):
        errors = validate_login_data(_valid_login())
        assert errors == []

    def test_login_accepts_short_password(self):
        """Login validation does not check password length."""
        errors = validate_login_data(_valid_login(password="x"))
        assert errors == []

    def test_login_accepts_invalid_email_format(self):
        """Login validation does not check email format."""
        errors = validate_login_data(_valid_login(email="not-an-email"))
        assert errors == []

    # --- Email field -------------------------------------------------------

    def test_missing_email(self):
        errors = validate_login_data({"password": "test"})
        assert any("email" in e for e in errors)

    def test_empty_email(self):
        errors = validate_login_data(_valid_login(email=""))
        assert any("email" in e for e in errors)

    def test_whitespace_only_email(self):
        errors = validate_login_data(_valid_login(email="   "))
        assert any("email" in e for e in errors)

    def test_null_email(self):
        errors = validate_login_data(_valid_login(email=None))
        assert any("email" in e for e in errors)

    # --- Password field ----------------------------------------------------

    def test_missing_password(self):
        errors = validate_login_data({"email": "test@example.com"})
        assert any("password" in e for e in errors)

    def test_empty_password(self):
        errors = validate_login_data(_valid_login(password=""))
        assert any("password" in e for e in errors)

    def test_null_password(self):
        errors = validate_login_data(_valid_login(password=None))
        assert any("password" in e for e in errors)

    # --- Non-dict input ----------------------------------------------------

    def test_non_dict_input(self):
        errors = validate_login_data("not a dict")
        assert any("JSON object" in e for e in errors)

    # --- Both missing ------------------------------------------------------

    def test_both_fields_missing(self):
        errors = validate_login_data({})
        assert len(errors) == 2

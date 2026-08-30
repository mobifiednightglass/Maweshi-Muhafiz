"""
AuthService — business logic for authentication operations.

Receives a UserRepository via constructor injection so the storage
backend can be swapped (in-memory → MongoDB) without touching this code.

Handles signup and login, including password hashing and JWT generation.
"""

from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories.base import UserRepository
from app.services.user_validation import validate_login_data, validate_signup_data

# handles the logic of login/signup(API endpoints)
# ---------------------------------------------------------------------------
# Custom exceptions — routes catch these and map to HTTP status codes
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when incoming data fails validation rules."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class DuplicateEmailError(Exception):
    """Raised when a signup attempt uses an already-registered email."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email '{email}' is already registered.")


class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid email or password.")


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AuthService:
    """Encapsulates all authentication-related business logic."""

    def __init__(self, repository: UserRepository, secret_key: str):
        self._repo = repository
        self._secret_key = secret_key

    # ---- Signup ---------------------------------------------------------

    def signup(self, data: dict) -> dict:
        """Register a new user and return user info + JWT token."""
        errors = validate_signup_data(data)
        if errors:
            raise ValidationError(errors)

        # Check for duplicate email
        existing = self._repo.get_by_email(data["email"])
        if existing is not None:
            raise DuplicateEmailError(data["email"])

        # Hash the password
        password_hash = generate_password_hash(data["password"])

        # Create the user
        user_data = {
            "name": data["name"],
            "email": data["email"],
            "password_hash": password_hash,
        }
        user = self._repo.create(user_data)

        # Remove password_hash from response
        user.pop("password_hash", None)
        # Generate JWT
        token = self._generate_token(user)

        return {
            "user": user,
            "token": token,
        }

    # ---- Login ----------------------------------------------------------

    def login(self, data: dict) -> dict:
        """Authenticate a user and return user info + JWT token."""
        errors = validate_login_data(data)
        if errors:
            raise ValidationError(errors)

        # Fetch user by email (includes password_hash)
        user = self._repo.get_by_email(data["email"])
        if user is None:
            raise AuthenticationError()

        # Verify password
        if not check_password_hash(user["password_hash"], data["password"]):
            raise AuthenticationError()

        # Remove password_hash from response
        user.pop("password_hash", None)

        # Generate JWT
        token = self._generate_token(user)

        return {
            "user": user,
            "token": token,
        }

    # ---- Helpers --------------------------------------------------------

    def _generate_token(self, user: dict) -> str:
        """Generate a JWT token for the given user."""
        payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

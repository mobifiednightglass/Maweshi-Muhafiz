"""
In-memory implementation of UserRepository.

Stores users in a plain Python dict keyed by auto-incrementing integer id.
Used for the "testing" config so the test suite runs fast without a live
database connection.
"""

from datetime import datetime, timezone
from typing import Optional

from app.repositories.base import UserRepository


class InMemoryUserRepository(UserRepository):
    """Dict-backed user repository with auto-incrementing IDs."""

    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id: int = 1
        self._email_index: dict[str, int] = {}  # email → id for uniqueness

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _to_public_dict(self, record: dict) -> dict:
        """Return a shallow copy without password_hash."""
        result = dict(record)
        result.pop("password_hash", None)
        return result

    def _to_internal_dict(self, record: dict) -> dict:
        """Return a shallow copy including password_hash."""
        return dict(record)

    @staticmethod
    def _to_int_id(user_id) -> Optional[int]:
        """Coerce an id to int; return None on failure."""
        try:
            return int(user_id)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        email = data["email"]

        # Check uniqueness
        if email in self._email_index:
            raise ValueError(f"Email '{email}' is already registered.")

        now = self._utcnow()
        record = {
            "id": self._next_id,
            "name": data["name"],
            "email": email,
            "password_hash": data["password_hash"],
            "created_at": now,
            "updated_at": now,
        }
        self._store[self._next_id] = record
        self._email_index[email] = self._next_id
        self._next_id += 1
        return self._to_public_dict(record)

    def get_by_id(self, user_id) -> Optional[dict]:
        int_id = self._to_int_id(user_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        return self._to_public_dict(record)

    def get_by_email(self, email: str) -> Optional[dict]:
        int_id = self._email_index.get(email)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        return self._to_internal_dict(record)

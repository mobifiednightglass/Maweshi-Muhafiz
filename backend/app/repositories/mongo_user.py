"""
MongoDB-backed implementation of UserRepository.

Stores users in the ``users`` collection of the configured MongoDB database.
Uses the same connection (MONGODB_URI / MONGODB_DB_NAME) as the animal
repository.  A unique index on ``email`` is created at initialisation time
to guarantee email uniqueness at the database level.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, MongoClient

from app.repositories.base import UserRepository

logger = logging.getLogger(__name__)


class MongoUserRepository(UserRepository):
    """MongoDB-backed user repository using pymongo."""

    def __init__(self, uri: str, db_name: str, collection_name: str = "users"):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        self._ensure_indexes()

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------

    def _ensure_indexes(self):
        """Create a unique index on email to enforce uniqueness at the DB level."""
        self._collection.create_index(
            [("email", ASCENDING)], unique=True, name="unique_email"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _to_object_id(user_id) -> Optional[ObjectId]:
        """Safely coerce an id value to ObjectId.  Returns None on failure."""
        if isinstance(user_id, ObjectId):
            return user_id
        try:
            return ObjectId(str(user_id))
        except (InvalidId, TypeError, ValueError):
            return None

    @staticmethod
    def _doc_to_public_dict(doc: dict) -> Optional[dict]:
        """Convert a MongoDB document to the public user dict (no password_hash)."""
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "name": doc.get("name"),
            "email": doc.get("email"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    @staticmethod
    def _doc_to_internal_dict(doc: dict) -> Optional[dict]:
        """Convert a MongoDB document to an internal dict (includes password_hash)."""
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "name": doc.get("name"),
            "email": doc.get("email"),
            "password_hash": doc.get("password_hash"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        doc = {
            "name": data["name"],
            "email": data["email"],
            "password_hash": data["password_hash"],
            "created_at": now,
            "updated_at": now,
        }

        result = self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._doc_to_public_dict(doc)

    def get_by_id(self, user_id) -> Optional[dict]:
        oid = self._to_object_id(user_id)
        if oid is None:
            return None
        doc = self._collection.find_one({"_id": oid})
        return self._doc_to_public_dict(doc) if doc else None

    def get_by_email(self, email: str) -> Optional[dict]:
        doc = self._collection.find_one({"email": email})
        return self._doc_to_internal_dict(doc) if doc else None

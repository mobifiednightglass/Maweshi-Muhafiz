"""
MongoDB-backed implementation of ReminderRepository.

Connects to the same MongoDB Atlas instance using MONGODB_URI and
MONGODB_DB_NAME from environment variables.  Stores documents in the
``reminders`` collection.  Uses ObjectId internally but always exposes
a plain string ``id`` field to the rest of the application.

A compound index on ``(user_id, animal_id)`` supports the per-animal
listing query.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

from app.repositories.base import ReminderRepository

logger = logging.getLogger(__name__)


class MongoReminderRepository(ReminderRepository):
    """MongoDB-backed reminder repository using pymongo."""

    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_name: str = "reminders",
    ):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        self._collection.create_index(
            [("user_id", 1), ("animal_id", 1)],
            name="idx_user_animal",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _to_object_id(value) -> Optional[ObjectId]:
        """Safely coerce an id value to ObjectId.  Returns None on failure."""
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(str(value))
        except (InvalidId, TypeError, ValueError):
            return None

    @staticmethod
    def _doc_to_dict(doc: dict) -> Optional[dict]:
        """Convert a raw MongoDB document to the app-level dict format.

        * Renames ``_id`` → ``id`` (as a plain string).
        * Maps only the known reminder keys.
        """
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "user_id": doc.get("user_id"),
            "animal_id": doc.get("animal_id"),
            "reminder_type": doc.get("reminder_type"),
            "due_date": doc.get("due_date"),
            "notes": doc.get("notes"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        doc = {
            "user_id": str(data.get("user_id")),
            "animal_id": str(data.get("animal_id")),
            "reminder_type": data.get("reminder_type"),
            "due_date": data.get("due_date"),
            "notes": data.get("notes"),
            "created_at": now,
            "updated_at": now,
        }

        result = self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._doc_to_dict(doc)

    def get_by_id(
        self, reminder_id, user_id,
    ) -> Optional[dict]:
        oid = self._to_object_id(reminder_id)
        if oid is None:
            return None
        doc = self._collection.find_one({
            "_id": oid,
            "user_id": str(user_id),
        })
        return self._doc_to_dict(doc) if doc else None

    def get_by_animal_id(
        self, animal_id, user_id,
    ) -> list[dict]:
        cursor = self._collection.find({
            "animal_id": str(animal_id),
            "user_id": str(user_id),
        })
        return [self._doc_to_dict(doc) for doc in cursor]

    def delete(
        self, reminder_id, user_id,
    ) -> bool:
        oid = self._to_object_id(reminder_id)
        if oid is None:
            return False
        result = self._collection.delete_one({
            "_id": oid,
            "user_id": str(user_id),
        })
        return result.deleted_count > 0

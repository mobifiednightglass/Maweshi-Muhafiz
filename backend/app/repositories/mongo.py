"""
MongoDB-backed implementation of AnimalRepository.

Connects to MongoDB Atlas using MONGODB_URI and MONGODB_DB_NAME from
environment variables.  Uses ObjectId internally but always exposes a
plain string ``id`` field to the rest of the application.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

from app.repositories.base import AnimalRepository

logger = logging.getLogger(__name__)

# Fields that callers may set on create / update
_MUTABLE_FIELDS = (
    "name",
    "animal_type",
    "breed",
    "gender",
    "age",
    "weight",
    "color",
    "health_status",
    "notes",
    "user_id",
)


class MongoAnimalRepository(AnimalRepository):
    """MongoDB-backed animal repository using pymongo."""

    def __init__(self, uri: str, db_name: str, collection_name: str = "animals"):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _to_object_id(animal_id) -> Optional[ObjectId]:
        """Safely coerce an id value to ObjectId.  Returns None on failure."""
        if isinstance(animal_id, ObjectId):
            return animal_id
        try:
            return ObjectId(str(animal_id))
        except (InvalidId, TypeError, ValueError):
            return None

    @staticmethod
    def _doc_to_dict(doc: dict) -> dict:
        """Convert a raw MongoDB document to the app-level dict format.

        * Renames ``_id`` → ``id`` (as a plain string).
        * Strips any keys not part of the Animal schema.
        """
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "user_id": str(doc.get("user_id")) if doc.get("user_id") is not None else None,
            "name": doc.get("name"),
            "animal_type": doc.get("animal_type"),
            "breed": doc.get("breed"),
            "gender": doc.get("gender"),
            "age": doc.get("age"),
            "weight": doc.get("weight"),
            "color": doc.get("color"),
            "health_status": doc.get("health_status"),
            "notes": doc.get("notes"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        doc = {field: data.get(field) for field in _MUTABLE_FIELDS}
        doc["created_at"] = now
        doc["updated_at"] = now

        result = self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._doc_to_dict(doc)

    def get_all(self, user_id=None) -> list[dict]:
        query = {}

        if user_id is not None:
            query["user_id"] = str(user_id)

        return [
            self._doc_to_dict(doc)
            for doc in self._collection.find(query)
        ]

    def get_by_id(self, animal_id, user_id=None) -> Optional[dict]:
        oid = self._to_object_id(animal_id)

        if oid is None:
            return None

        query = {"_id": oid}

        if user_id is not None:
            query["user_id"] = str(user_id)

        doc = self._collection.find_one(query)

        return self._doc_to_dict(doc) if doc else None

    def update(self, animal_id, data: dict, user_id=None) -> Optional[dict]:
        oid = self._to_object_id(animal_id)
        if oid is None:
            return None

        set_fields = {}
        for key in _MUTABLE_FIELDS:
            if key in data:
                set_fields[key] = data[key]

        if not set_fields:
            # Nothing to update — just return current state
            return self.get_by_id(animal_id, user_id=user_id)

        set_fields["updated_at"] = self._utcnow()

        query = {"_id": oid}
        if user_id is not None:
            query["user_id"] = str(user_id)

        result = self._collection.find_one_and_update(
            query,
            {"$set": set_fields},
            return_document=True,
        )
        return self._doc_to_dict(result) if result else None

    def delete(self, animal_id, user_id=None) -> bool:
        oid = self._to_object_id(animal_id)
        if oid is None:
            return False
        query = {"_id": oid}
        if user_id is not None:
            query["user_id"] = str(user_id)
        result = self._collection.delete_one(query)
        return result.deleted_count > 0

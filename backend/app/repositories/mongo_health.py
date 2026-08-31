"""
MongoDB-backed implementation of HealthAssessmentRepository.

Connects to the same MongoDB Atlas instance using MONGODB_URI and
MONGODB_DB_NAME from environment variables.  Stores documents in the
``health_assessments`` collection.  Uses ObjectId internally but always
exposes a plain string ``id`` field to the rest of the application.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

from app.repositories.base import HealthAssessmentRepository

logger = logging.getLogger(__name__)

# Fields that callers may set on create / update
_MUTABLE_FIELDS = (
    "animal_id",
    "symptoms",
    "image_ids",
    "diagnosis_result",
    "status",
)

_VALID_STATUSES = ("pending", "completed", "failed")


class MongoHealthAssessmentRepository(HealthAssessmentRepository):
    """MongoDB-backed health-assessment repository using pymongo."""

    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_name: str = "health_assessments",
    ):
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
        * Maps only the known HealthAssessment keys.
        """
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "animal_id": doc.get("animal_id"),
            "symptoms": doc.get("symptoms"),
            "image_ids": doc.get("image_ids", []),
            "diagnosis_result": doc.get("diagnosis_result"),
            "status": doc.get("status", "pending"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            # Red-flag assessment fields
            "is_red_flag": doc.get("is_red_flag", False),
            "red_flag_reasons": doc.get("red_flag_reasons", []),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        doc = {field: data.get(field) for field in _MUTABLE_FIELDS}
        doc["is_red_flag"] = data.get("is_red_flag", False)
        doc["red_flag_reasons"] = data.get("red_flag_reasons", [])
        # Defaults
        if doc.get("image_ids") is None:
            doc["image_ids"] = []
        if doc.get("status") is None:
            doc["status"] = "pending"

        doc["created_at"] = now
        doc["updated_at"] = now

        result = self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._doc_to_dict(doc)

    def get_by_id(self, assessment_id) -> Optional[dict]:
        oid = self._to_object_id(assessment_id)
        if oid is None:
            return None
        doc = self._collection.find_one({"_id": oid})
        return self._doc_to_dict(doc) if doc else None

    def get_by_animal_id(self, animal_id) -> list[dict]:
        # animal_id is persisted as a plain string (from validated input)
        cursor = self._collection.find({"animal_id": str(animal_id)})
        return [self._doc_to_dict(doc) for doc in cursor]

    def update(self, assessment_id, data: dict) -> Optional[dict]:
        oid = self._to_object_id(assessment_id)
        if oid is None:
            return None

        set_fields = {}
        for key in _MUTABLE_FIELDS:
            if key in data:
                set_fields[key] = data[key]
        set_fields["updated_at"] = self._utcnow()
        set_fields["is_red_flag"] = data.get("is_red_flag", False)
        set_fields["red_flag_reasons"] = data.get("red_flag_reasons", [])
        if not set_fields:
            # Nothing to update — just return current state
            return self.get_by_id(assessment_id, user_id=data.get("user_id"))

        result = self._collection.find_one_and_update(
            {"_id": oid},
            {"$set": set_fields},
            return_document=True,
        )
        return self._doc_to_dict(result) if result else None

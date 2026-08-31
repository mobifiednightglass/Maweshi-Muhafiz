"""
MongoDB-backed implementation of VetCaseSummaryRepository.

Connects to the same MongoDB Atlas instance using MONGODB_URI and
MONGODB_DB_NAME from environment variables.  Stores documents in the
``vet_case_summaries`` collection.  Uses ObjectId internally but always
exposes a plain string ``id`` field to the rest of the application.

A unique compound index on ``(user_id, assessment_id)`` prevents
duplicate summaries for the same assessment by the same user.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from app.repositories.base import VetCaseSummaryRepository

logger = logging.getLogger(__name__)

# Assessment fields snapshotted into the summary document
_ASSESSMENT_SNAPSHOT_FIELDS = (
    "symptoms",
    "image_ids",
    "diagnosis_result",
    "status",
    "is_red_flag",
    "red_flag_reasons",
)


class MongoVetCaseSummaryRepository(VetCaseSummaryRepository):
    """MongoDB-backed vet case summary repository using pymongo."""

    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_name: str = "vet_case_summaries",
    ):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        # Prevent duplicate summaries for the same (user, assessment) pair
        self._collection.create_index(
            [("user_id", 1), ("assessment_id", 1)],
            unique=True,
            name="uniq_user_assessment",
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
        * Maps only the known VetCaseSummary keys.
        """
        if doc is None:
            return None
        return {
            "id": str(doc["_id"]),
            "user_id": doc.get("user_id"),
            "animal_id": doc.get("animal_id"),
            "assessment_id": doc.get("assessment_id"),
            "created_at": doc.get("created_at"),
            # Snapshotted assessment fields
            "symptoms": doc.get("symptoms"),
            "image_ids": doc.get("image_ids", []),
            "diagnosis_result": doc.get("diagnosis_result"),
            "status": doc.get("status"),
            "is_red_flag": doc.get("is_red_flag", False),
            "red_flag_reasons": doc.get("red_flag_reasons", []),
            # Snapshotted animal details
            "animal": doc.get("animal"),
        }

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        doc = {
            "user_id": str(data.get("user_id")),
            "animal_id": str(data.get("animal_id")),
            "assessment_id": str(data.get("assessment_id")),
            "created_at": now,
        }
        # Snapshot the relevant assessment fields
        for field in _ASSESSMENT_SNAPSHOT_FIELDS:
            doc[field] = data.get(field)

        # Snapshot the animal details
        doc["animal"] = data.get("animal")

        try:
            result = self._collection.insert_one(doc)
        except DuplicateKeyError:
            logger.warning(
                "Duplicate vet summary for user=%s assessment=%s",
                doc["user_id"],
                doc["assessment_id"],
            )
            # Return the existing summary instead of raising
            existing = self.get_by_assessment_id(
                doc["assessment_id"], doc["user_id"],
            )
            if existing is not None:
                return existing
            raise  # should not happen, but re-raise if it does

        doc["_id"] = result.inserted_id
        return self._doc_to_dict(doc)

    def get_by_id(
        self, summary_id, user_id,
    ) -> Optional[dict]:
        oid = self._to_object_id(summary_id)
        if oid is None:
            return None
        doc = self._collection.find_one({
            "_id": oid,
            "user_id": str(user_id),
        })
        return self._doc_to_dict(doc) if doc else None

    def get_by_user_id(self, user_id) -> list[dict]:
        cursor = self._collection.find({"user_id": str(user_id)})
        return [self._doc_to_dict(doc) for doc in cursor]

    def get_by_assessment_id(
        self, assessment_id, user_id,
    ) -> Optional[dict]:
        doc = self._collection.find_one({
            "assessment_id": str(assessment_id),
            "user_id": str(user_id),
        })
        return self._doc_to_dict(doc) if doc else None

    def update_animal(
        self, assessment_id, user_id, animal,
    ) -> Optional[dict]:
        result = self._collection.find_one_and_update(
            {
                "assessment_id": str(assessment_id),
                "user_id": str(user_id),
            },
            {"$set": {"animal": animal}},
            return_document=True,
        )
        return self._doc_to_dict(result) if result else None

    def delete(
        self, summary_id, user_id,
    ) -> bool:
        oid = self._to_object_id(summary_id)
        if oid is None:
            return False
        result = self._collection.delete_one({
            "_id": oid,
            "user_id": str(user_id),
        })
        return result.deleted_count > 0

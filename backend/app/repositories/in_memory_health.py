"""
In-memory implementation of HealthAssessmentRepository.

Stores assessments in a plain Python dict keyed by auto-incrementing
integer id.  Used for the "testing" config so the test suite runs fast
without a live database connection.
"""

from datetime import datetime, timezone
from typing import Optional, Union

from app.repositories.base import EntityId, HealthAssessmentRepository


class InMemoryHealthAssessmentRepository(HealthAssessmentRepository):
    """Dict-backed health-assessment repository with auto-incrementing IDs."""

    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _to_dict(self, record: dict) -> dict:
        """Return a shallow copy so callers cannot mutate the store."""
        return dict(record)

    @staticmethod
    def _to_int_id(value: EntityId) -> Optional[int]:
        """Coerce an id to int; return None on failure."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        record = {
            "id": self._next_id,
            "animal_id": data.get("animal_id"),
            "symptoms": data.get("symptoms"),
            "image_ids": data.get("image_ids", []),
            "diagnosis_result": data.get("diagnosis_result"),
            "status": data.get("status", "pending"),
            "created_at": now,
            "updated_at": now,
        }
        self._store[self._next_id] = record
        self._next_id += 1
        return self._to_dict(record)

    def get_by_id(self, assessment_id: EntityId) -> Optional[dict]:
        int_id = self._to_int_id(assessment_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        return self._to_dict(record)

    def get_by_animal_id(self, animal_id: EntityId) -> list[dict]:
        return [
            self._to_dict(r)
            for r in self._store.values()
            if str(r.get("animal_id")) == str(animal_id)
        ]

    def update(self, assessment_id: EntityId, data: dict) -> Optional[dict]:
        int_id = self._to_int_id(assessment_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        for key in ("animal_id", "symptoms", "image_ids", "diagnosis_result", "status"):
            if key in data:
                record[key] = data[key]
        record["updated_at"] = self._utcnow()
        return self._to_dict(record)

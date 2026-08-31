"""
In-memory implementation of VetCaseSummaryRepository.

Stores summaries in a plain Python dict keyed by auto-incrementing
integer id.  Used for the "testing" config so the test suite runs fast
without a live database connection.
"""

from datetime import datetime, timezone
from typing import Optional

from app.repositories.base import EntityId, VetCaseSummaryRepository

# Assessment fields that are snapshotted into the summary
_ASSESSMENT_SNAPSHOT_FIELDS = (
    "symptoms",
    "image_ids",
    "diagnosis_result",
    "status",
    "is_red_flag",
    "red_flag_reasons",
)


class InMemoryVetCaseSummaryRepository(VetCaseSummaryRepository):
    """Dict-backed vet case summary repository with auto-incrementing IDs."""

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
            "user_id": str(data.get("user_id")),
            "animal_id": str(data.get("animal_id")),
            "assessment_id": str(data.get("assessment_id")),
            "created_at": now,
        }
        # Snapshot the relevant assessment fields
        for field in _ASSESSMENT_SNAPSHOT_FIELDS:
            record[field] = data.get(field)

        # Snapshot the animal details
        record["animal"] = data.get("animal")

        self._store[self._next_id] = record
        self._next_id += 1
        return self._to_dict(record)

    def get_by_id(
        self, summary_id: EntityId, user_id: EntityId,
    ) -> Optional[dict]:
        int_id = self._to_int_id(summary_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        if str(record.get("user_id")) != str(user_id):
            return None
        return self._to_dict(record)

    def get_by_user_id(self, user_id: EntityId) -> list[dict]:
        return [
            self._to_dict(r)
            for r in self._store.values()
            if str(r.get("user_id")) == str(user_id)
        ]

    def get_by_assessment_id(
        self, assessment_id: EntityId, user_id: EntityId,
    ) -> Optional[dict]:
        for r in self._store.values():
            if (
                str(r.get("assessment_id")) == str(assessment_id)
                and str(r.get("user_id")) == str(user_id)
            ):
                return self._to_dict(r)
        return None

    def update_animal(
        self, assessment_id: EntityId, user_id: EntityId, animal: dict,
    ) -> Optional[dict]:
        for r in self._store.values():
            if (
                str(r.get("assessment_id")) == str(assessment_id)
                and str(r.get("user_id")) == str(user_id)
            ):
                r["animal"] = animal
                return self._to_dict(r)
        return None

    def delete(
        self, summary_id: EntityId, user_id: EntityId,
    ) -> bool:
        int_id = self._to_int_id(summary_id)
        if int_id is None:
            return False
        record = self._store.get(int_id)
        if record is None:
            return False
        if str(record.get("user_id")) != str(user_id):
            return False
        del self._store[int_id]
        return True

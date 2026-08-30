"""
In-memory implementation of AnimalRepository.

Stores animals in a plain Python dict keyed by auto-incrementing integer id.
Used for the "testing" config so the test suite runs fast without a live
database connection.
"""

from datetime import datetime, timezone
from typing import Optional, Union

from app.repositories.base import AnimalId, AnimalRepository


class InMemoryAnimalRepository(AnimalRepository):
    """Dict-backed animal repository with auto-incrementing IDs."""

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
    def _to_int_id(animal_id: AnimalId) -> Optional[int]:
        """Coerce an id to int; return None on failure."""
        try:
            return int(animal_id)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def create(self, data: dict) -> dict:
        now = self._utcnow()
        record = {
            "id": self._next_id,
            "name": data["name"],
            "animal_type": data["animal_type"],
            "breed": data.get("breed"),
            "gender": data.get("gender"),
            "age": data.get("age"),
            "weight": data.get("weight"),
            "color": data.get("color"),
            "health_status": data.get("health_status"),
            "notes": data.get("notes"),
            "created_at": now,
            "updated_at": now,
        }
        self._store[self._next_id] = record
        self._next_id += 1
        return self._to_dict(record)

    def get_all(self) -> list[dict]:
        return [self._to_dict(r) for r in self._store.values()]

    def get_by_id(self, animal_id: AnimalId) -> Optional[dict]:
        int_id = self._to_int_id(animal_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        return self._to_dict(record)

    def update(self, animal_id: AnimalId, data: dict) -> Optional[dict]:
        int_id = self._to_int_id(animal_id)
        if int_id is None:
            return None
        record = self._store.get(int_id)
        if record is None:
            return None
        # Only overwrite fields that were explicitly provided
        for key in (
            "name",
            "animal_type",
            "breed",
            "gender",
            "age",
            "weight",
            "color",
            "health_status",
            "notes",
        ):
            if key in data:
                record[key] = data[key]
        record["updated_at"] = self._utcnow()
        return self._to_dict(record)

    def delete(self, animal_id: AnimalId) -> bool:
        int_id = self._to_int_id(animal_id)
        if int_id is None:
            return False
        if int_id not in self._store:
            return False
        del self._store[int_id]
        return True

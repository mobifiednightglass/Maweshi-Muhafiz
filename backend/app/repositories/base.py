"""
Abstract base classes for data access.

Every concrete repository (in-memory, MongoDB, etc.) must implement the
relevant interface so the service layer can remain storage-agnostic.

``animal_id`` / ``user_id`` parameters accept both ``int`` and ``str`` so
that the interface works with auto-increment IDs (in-memory) and ObjectIds
(MongoDB) without the service or route layers needing to know which
backend is active.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union


EntityId = Union[int, str]

# Backward-compatible alias
AnimalId = EntityId


# ---------------------------------------------------------------------------
# Animal repository interface
# ---------------------------------------------------------------------------

class AnimalRepository(ABC):
    """Interface that all animal repositories must satisfy."""

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Persist a new animal record and return the created entity as a dict.

        The repository is responsible for assigning an ``id`` and setting
        ``created_at`` / ``updated_at`` timestamps.
        """

    @abstractmethod
    def get_all(self) -> list[dict]:
        """Return every animal record as a list of dicts."""

    @abstractmethod
    def get_by_id(self, animal_id: EntityId) -> Optional[dict]:
        """Return a single animal by its id, or ``None`` if not found."""

    @abstractmethod
    def update(self, animal_id: EntityId, data: dict) -> Optional[dict]:
        """Update an existing animal record.

        Returns the updated dict, or ``None`` if the id does not exist.
        The repository must refresh ``updated_at``.
        """

    @abstractmethod
    def delete(self, animal_id: EntityId) -> bool:
        """Delete an animal record.

        Returns ``True`` if a record was removed, ``False`` if the id
        did not exist.
        """


# ---------------------------------------------------------------------------
# User repository interface
# ---------------------------------------------------------------------------

class UserRepository(ABC):
    """Interface that all user repositories must satisfy."""

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Persist a new user record and return the created entity as a dict.

        The repository is responsible for assigning an ``id`` and setting
        ``created_at`` / ``updated_at`` timestamps.

        The ``data`` dict is expected to contain ``name``, ``email``, and
        ``password_hash`` (never a plain-text password).
        """

    @abstractmethod
    def get_by_id(self, user_id: EntityId) -> Optional[dict]:
        """Return a single user by its id, or ``None`` if not found.

        The returned dict must NOT include the ``password_hash`` field.
        """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[dict]:
        """Return a single user by email, or ``None`` if not found.

        The returned dict MUST include ``password_hash`` so that the
        authentication layer can verify the password.
        """


# ---------------------------------------------------------------------------
# Health-assessment repository interface
# ---------------------------------------------------------------------------

class HealthAssessmentRepository(ABC):
    """Interface that all health-assessment repositories must satisfy."""

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Persist a new health-assessment record and return it as a dict.

        The repository is responsible for assigning an ``id`` and setting
        ``created_at`` / ``updated_at`` timestamps.
        """

    @abstractmethod
    def get_by_id(self, assessment_id: EntityId) -> Optional[dict]:
        """Return a single health assessment by its id, or ``None``."""

    @abstractmethod
    def get_by_animal_id(self, animal_id: EntityId) -> list[dict]:
        """Return all health assessments for a given animal (may be empty)."""

    @abstractmethod
    def update(self, assessment_id: EntityId, data: dict) -> Optional[dict]:
        """Update an existing health-assessment record.

        Returns the updated dict, or ``None`` if the id does not exist.
        The repository must refresh ``updated_at``.
        """

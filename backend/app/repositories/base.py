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

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Create an animal."""

    @abstractmethod
    def get_all(self, user_id=None) -> list[dict]:
        """Return animals belonging to the specified user."""

    @abstractmethod
    def get_by_id(self, animal_id: EntityId, user_id=None) -> Optional[dict]:
        """Return an animal only if it belongs to the specified user."""

    @abstractmethod
    def update(
        self,
        animal_id: EntityId,
        data: dict,
        user_id=None
    ) -> Optional[dict]:
        """Update an animal only if it belongs to the specified user."""

    @abstractmethod
    def delete(self, animal_id: EntityId, user_id=None) -> bool:
        """Delete an animal only if it belongs to the specified user."""


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
    def get_by_image_id(self, image_id: str) -> Optional[dict]:
        """Return the first health assessment referencing *image_id*, or ``None``."""

    @abstractmethod
    def update(self, assessment_id: EntityId, data: dict) -> Optional[dict]:
        """Update an existing health-assessment record.

        Returns the updated dict, or ``None`` if the id does not exist.
        The repository must refresh ``updated_at``.
        """


# ---------------------------------------------------------------------------
# Vet-ready case summary repository interface
# ---------------------------------------------------------------------------

class VetCaseSummaryRepository(ABC):
    """Interface for persisting Vet-Ready Case Summaries.

    A summary is a snapshot of a completed health assessment, owned by
    the authenticated user who created it.  Every lookup is scoped to
    ``user_id`` so users can only access their own summaries.
    """

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Persist a new vet case summary and return it as a dict.

        ``data`` must contain ``user_id``, ``animal_id``, and
        ``assessment_id``.  The repository assigns ``id`` and
        ``created_at``.
        """

    @abstractmethod
    def get_by_id(
        self, summary_id: EntityId, user_id: EntityId,
    ) -> Optional[dict]:
        """Return a single summary only if it belongs to *user_id*."""

    @abstractmethod
    def get_by_user_id(self, user_id: EntityId) -> list[dict]:
        """Return all summaries belonging to *user_id* (may be empty)."""

    @abstractmethod
    def get_by_assessment_id(
        self, assessment_id: EntityId, user_id: EntityId,
    ) -> Optional[dict]:
        """Return the summary for a specific assessment, scoped to *user_id*."""

    @abstractmethod
    def update_animal(
        self, assessment_id: EntityId, user_id: EntityId, animal: dict,
    ) -> Optional[dict]:
        """Update the animal snapshot on an existing summary.

        Returns the updated summary, or ``None`` if not found.
        """

    @abstractmethod
    def delete(
        self, summary_id: EntityId, user_id: EntityId,
    ) -> bool:
        """Delete a summary only if it belongs to *user_id*.

        Returns ``True`` if a document was deleted, ``False`` otherwise.
        """


# ---------------------------------------------------------------------------
# Animal health reminder repository interface
# ---------------------------------------------------------------------------

class ReminderRepository(ABC):
    """Interface for persisting animal health reminders.

    A reminder (e.g. vaccination, deworming) is attached to an animal and
    owned by the authenticated user who created it.  Every lookup is
    scoped to ``user_id`` so users can only access their own reminders.
    """

    @abstractmethod
    def create(self, data: dict) -> dict:
        """Persist a new reminder and return it as a dict.

        ``data`` must contain ``user_id``, ``animal_id``, ``reminder_type``,
        and ``due_date``; ``notes`` is optional.  The repository assigns
        ``id`` and ``created_at`` / ``updated_at``.
        """

    @abstractmethod
    def get_by_id(
        self, reminder_id: EntityId, user_id: EntityId,
    ) -> Optional[dict]:
        """Return a single reminder only if it belongs to *user_id*."""

    @abstractmethod
    def get_by_animal_id(
        self, animal_id: EntityId, user_id: EntityId,
    ) -> list[dict]:
        """Return all reminders for an animal belonging to *user_id*."""

    @abstractmethod
    def delete(
        self, reminder_id: EntityId, user_id: EntityId,
    ) -> bool:
        """Delete a reminder only if it belongs to *user_id*.

        Returns ``True`` if a record was deleted, ``False`` otherwise.
        """

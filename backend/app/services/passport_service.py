"""
PassportService — composes the animal "health passport" view.

A passport bundles, for a single animal owned by the requesting user:
  * the animal's profile,
  * the complete health-assessment history,
  * any vet case summaries linked to those assessments,
  * the animal's reminders, split into upcoming and past by due date.

The service is read-only and owns no storage of its own — it composes
the already-wired animal service and the assessment, vet-summary, and
reminder repositories.
"""

from datetime import datetime, timezone
from typing import Optional

from app.repositories.base import (
    HealthAssessmentRepository,
    ReminderRepository,
    VetCaseSummaryRepository,
)
from app.services.animal_service import AnimalService


class PassportService:
    """Encapsulates the read-only composition logic for animal passports."""

    def __init__(
        self,
        animal_service: AnimalService,
        health_assessment_repo: HealthAssessmentRepository,
        vet_summary_repo: VetCaseSummaryRepository,
        reminder_repo: ReminderRepository,
    ):
        self._animal_service = animal_service
        self._health_assessment_repo = health_assessment_repo
        self._vet_summary_repo = vet_summary_repo
        self._reminder_repo = reminder_repo

    # ---- Read -----------------------------------------------------------

    def get_passport(self, animal_id, user_id) -> dict:
        """Build the combined passport for one animal.

        Raises ``AnimalNotFoundError`` when the animal does not exist or
        does not belong to *user_id*.
        """
        # Ownership check first — everything else is scoped to this animal.
        animal = self._animal_service.get_by_id(animal_id, user_id)
        animal_key = str(animal["id"])

        assessments = self._health_assessment_repo.get_by_animal_id(animal_key)

        vet_case_summaries = []
        for assessment in assessments:
            summary = self._vet_summary_repo.get_by_assessment_id(
                assessment["id"], user_id
            )
            if summary is not None:
                vet_case_summaries.append(summary)

        reminders = self._reminder_repo.get_by_animal_id(animal_key, user_id)
        upcoming, past = self._split_reminders(reminders)

        return {
            "animal": animal,
            "assessments": assessments,
            "vet_case_summaries": vet_case_summaries,
            "reminders": {"upcoming": upcoming, "past": past},
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_reminders(
        reminders: list[dict],
    ) -> tuple[list[dict], list[dict]]:
        """Split reminders into (upcoming, past) relative to now."""
        now = datetime.now(timezone.utc)
        upcoming: list[dict] = []
        past: list[dict] = []
        for reminder in reminders:
            due = PassportService._parse_due_date(reminder.get("due_date"))
            # Unparseable dates are kept visible under "upcoming".
            if due is None or due >= now:
                upcoming.append(reminder)
            else:
                past.append(reminder)
        return upcoming, past

    @staticmethod
    def _parse_due_date(value) -> Optional[datetime]:
        """Parse an ISO-8601 due date; return ``None`` if unparseable."""
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        # Date-only strings parse naive; assume UTC so comparing against
        # the timezone-aware "now" above cannot raise TypeError.
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

"""
HealthCardService — builds a simplified, buyer-facing animal health card.

The health card is intentionally redacted: it shows only the animal's basic
identity, current preventive-care standing (vaccination / deworming / other
reminders), and whether the most recent health assessment raised an active
warning. It omits diagnosis details, symptom history, private notes, and the
full assessment record.
"""

from datetime import datetime, timezone
from typing import Optional

from app.repositories.base import HealthAssessmentRepository, ReminderRepository
from app.services.animal_service import AnimalNotFoundError, AnimalService
from app.services.insight_service import InsightService
from app.services.passport_service import PassportService


class HealthCardService:
    """Encapsulates read-only composition logic for buyer-facing health cards."""

    def __init__(
        self,
        animal_service: AnimalService,
        health_assessment_repo: HealthAssessmentRepository,
        reminder_repo: ReminderRepository,
    ):
        self._animal_service = animal_service
        self._health_assessment_repo = health_assessment_repo
        self._reminder_repo = reminder_repo

    # ---- Read -----------------------------------------------------------

    def get_health_card(self, animal_id, user_id) -> dict:
        """Build a buyer-facing health card for one animal.

        Raises ``AnimalNotFoundError`` when the animal does not exist or
        does not belong to *user_id*.
        """
        animal = self._animal_service.get_by_id(animal_id, user_id)
        animal_key = str(animal["id"])

        reminders = self._reminder_repo.get_by_animal_id(animal_key, user_id)
        preventive_care = self._build_preventive_care(reminders)

        assessments = self._health_assessment_repo.get_by_animal_id(animal_key)
        health_warnings = self._build_health_warnings(assessments)

        return {
            "animal": {
                "id": animal_key,
                "name": animal.get("name"),
                "animal_type": animal.get("animal_type"),
            },
            "preventive_care": preventive_care,
            "health_warnings": health_warnings,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_preventive_care(self, reminders: list[dict]) -> dict:
        """Categorize reminders and compute an overall preventive-care status."""
        now = datetime.now(timezone.utc)

        vaccination_reminders = []
        deworming_reminders = []
        other_reminders = []

        for reminder in reminders:
            category = self._categorize_reminder(reminder.get("reminder_type"))
            if category == "vaccination":
                vaccination_reminders.append(reminder)
            elif category == "deworming":
                deworming_reminders.append(reminder)
            else:
                other_reminders.append(reminder)

        vaccination = self._summarize_category(vaccination_reminders, now)
        deworming = self._summarize_category(deworming_reminders, now)
        other = [
            self._summarize_category([reminder], now)
            for reminder in other_reminders
        ]

        status = self._overall_preventive_status(
            vaccination, deworming, other, bool(reminders)
        )

        return {
            "status": status,
            "vaccination": vaccination,
            "deworming": deworming,
            "other": other,
        }

    @staticmethod
    def _categorize_reminder(reminder_type: Optional[str]) -> str:
        """Bucket a reminder into vaccination, deworming, or other."""
        t = (reminder_type or "").strip().lower()
        if "vaccin" in t or "booster" in t:
            return "vaccination"
        if "deworm" in t or "worm" in t:
            return "deworming"
        return "other"

    def _summarize_category(
        self, reminders: list[dict], now: datetime
    ) -> dict:
        """Return the status of a category based on its latest reminder."""
        if not reminders:
            return {
                "reminder_type": None,
                "status": "not_recorded",
                "due_date": None,
                "days_overdue": None,
            }

        latest = max(
            reminders,
            key=lambda r: (
                PassportService._parse_due_date(r.get("due_date"))
                or datetime.min.replace(tzinfo=timezone.utc),
                str(r.get("id")),
            ),
        )

        base = {
            "reminder_type": latest.get("reminder_type"),
            "due_date": latest.get("due_date"),
        }

        due = PassportService._parse_due_date(latest.get("due_date"))
        if due is None:
            return {
                **base,
                "status": "not_recorded",
                "days_overdue": None,
            }

        if due >= now:
            return {
                **base,
                "status": "up_to_date",
                "days_overdue": None,
            }

        return {
            **base,
            "status": "overdue",
            "days_overdue": (now - due).days,
        }

    @staticmethod
    def _overall_preventive_status(
        vaccination: dict,
        deworming: dict,
        other: list[dict],
        has_any_reminders: bool,
    ) -> str:
        """Derive the overall preventive-care status."""
        if not has_any_reminders:
            return "unknown"

        entries = [vaccination, deworming, *other]
        if any(entry["status"] == "overdue" for entry in entries):
            return "attention_needed"

        if all(entry["status"] == "not_recorded" for entry in entries):
            return "unknown"

        return "up_to_date"

    def _build_health_warnings(self, assessments: list[dict]) -> dict:
        """Derive the active-warning summary from the most recent assessment."""
        if not assessments:
            return {
                "has_active_warning": False,
                "urgency_level": None,
                "last_assessed_at": None,
            }

        latest = max(
            assessments,
            key=lambda a: (
                self._parse_created_at(a.get("created_at")),
                str(a.get("id")),
            ),
        )

        has_active_warning = InsightService._is_flagged(latest)
        urgency_level = self._extract_urgency(latest)

        return {
            "has_active_warning": has_active_warning,
            "urgency_level": urgency_level,
            "last_assessed_at": latest.get("created_at"),
        }

    @staticmethod
    def _parse_created_at(value) -> datetime:
        """Parse an ISO-8601 created_at timestamp; return a safe minimum on failure."""
        if not isinstance(value, str):
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    @staticmethod
    def _extract_urgency(assessment: dict) -> Optional[str]:
        """Return the normalized urgency level from an assessment, if present."""
        diagnosis = assessment.get("diagnosis_result")
        if not isinstance(diagnosis, dict):
            return None
        urgency = diagnosis.get("urgency_level")
        if isinstance(urgency, str):
            return urgency.lower()
        return None

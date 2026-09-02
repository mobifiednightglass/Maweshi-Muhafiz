"""
ReminderService — business logic for animal health reminders.
"""

from app.repositories.base import ReminderRepository
from app.services.reminder_validation import validate_reminder_data


class ValidationError(Exception):
    """Raised when incoming data fails validation rules."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class ReminderNotFoundError(Exception):
    """Raised when a requested reminder does not exist or is not owned by the user."""

    def __init__(self, reminder_id):
        self.reminder_id = reminder_id
        super().__init__(f"Reminder with id {reminder_id} not found.")


class ReminderService:
    """Encapsulates all reminder-related business logic."""

    def __init__(self, repository: ReminderRepository):
        self._repo = repository

    # ---- Create ---------------------------------------------------------

    def create(self, data: dict, animal_id, user_id) -> dict:
        errors = validate_reminder_data(data)

        if errors:
            raise ValidationError(errors)

        # Never trust user_id / animal_id coming from the client.
        # Ownership comes from the authenticated user and the URL.
        reminder_data = dict(data)
        reminder_data["user_id"] = user_id
        reminder_data["animal_id"] = animal_id

        return self._repo.create(reminder_data)

    # ---- Read -----------------------------------------------------------

    def get_by_animal_id(self, animal_id, user_id) -> list[dict]:
        return self._repo.get_by_animal_id(animal_id, user_id=user_id)

    def get_by_id(self, reminder_id, user_id) -> dict:
        record = self._repo.get_by_id(reminder_id, user_id=user_id)

        if record is None:
            raise ReminderNotFoundError(reminder_id)

        return record

    # ---- Delete ---------------------------------------------------------

    def delete(self, reminder_id, user_id) -> bool:
        if not self._repo.delete(reminder_id, user_id=user_id):
            raise ReminderNotFoundError(reminder_id)

        return True

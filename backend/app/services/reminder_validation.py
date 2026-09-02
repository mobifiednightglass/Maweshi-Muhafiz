"""
Reminder data validation — standalone, reusable by any route or service layer.

Validates plain dictionaries (e.g. parsed JSON request bodies) against the
rules defined for the Reminder model.  Returns a list of human-readable
error strings; an empty list means the data is valid.

Usage:
    errors = validate_reminder_data(data)
    if errors:
        # return 400 with errors
"""
from datetime import datetime

# ---------------------------------------------------------------------------
# Field constraints
# ---------------------------------------------------------------------------
MAX_REMINDER_TYPE_LENGTH = 50
MAX_NOTES_LENGTH = 2000

REQUIRED_FIELDS = ("reminder_type", "due_date")

# Fields the client is allowed to submit (id/timestamps/ownership are
# server-managed)
ALLOWED_FIELDS = {
    "reminder_type",
    "due_date",
    "notes",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_reminder_data(data: dict) -> list[str]:
    """Validate a reminder data dictionary.

    Parameters
    ----------
    data : dict
        The incoming payload to validate.

    Returns
    -------
    list[str]
        A list of error messages.  Empty list == data is valid.

    Notes
    -----
    ``due_date`` accepts any ISO-8601 date or datetime string
    (``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SS``).  Dates in the past are
    allowed — users may legitimately record an overdue reminder.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    # --- Required field checks --------------------------------------------
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"'{field}' is required.")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"'{field}' must not be empty.")

    # --- Type & constraint checks for every provided field ----------------
    for field in data:
        if field not in ALLOWED_FIELDS:
            errors.append(f"Unknown field '{field}'.")
            continue

        value = data[field]

        # Skip further checks for null/None on optional fields
        if value is None:
            if field in REQUIRED_FIELDS:
                errors.append(f"'{field}' must not be null.")
            continue

        if field == "reminder_type":
            if not isinstance(value, str):
                errors.append("'reminder_type' must be a string.")
                continue
            if not value.strip():
                errors.append("'reminder_type' must not be empty.")
                continue
            if len(value) > MAX_REMINDER_TYPE_LENGTH:
                errors.append(
                    "'reminder_type' must be at most "
                    f"{MAX_REMINDER_TYPE_LENGTH} characters long."
                )

        elif field == "due_date":
            if not isinstance(value, str):
                errors.append("'due_date' must be a string.")
                continue
            try:
                datetime.fromisoformat(value)
            except ValueError:
                errors.append(
                    "'due_date' must be a valid ISO date "
                    "(YYYY-MM-DD) or ISO datetime string."
                )

        elif field == "notes":
            if not isinstance(value, str):
                errors.append("'notes' must be a string.")
            elif len(value) > MAX_NOTES_LENGTH:
                errors.append(
                    f"'notes' must be at most {MAX_NOTES_LENGTH} characters long."
                )

    return errors

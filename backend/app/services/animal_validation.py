"""
Animal data validation — standalone, reusable by any route or service layer.

Validates plain dictionaries (e.g. parsed JSON request bodies) against the
rules defined for the Animal model.  Returns a list of human-readable error
strings; an empty list means the data is valid.

Usage:
    errors = validate_animal_data(data)
    if errors:
        # return 400 with errors
"""

# ---------------------------------------------------------------------------
# Field constraints — single source of truth, mirrors app/models/animal.py
# ---------------------------------------------------------------------------
MAX_NAME_LENGTH = 100
MAX_ANIMAL_TYPE_LENGTH = 50
MAX_BREED_LENGTH = 100
MAX_GENDER_LENGTH = 20
MAX_COLOR_LENGTH = 50
MAX_HEALTH_STATUS_LENGTH = 50
MAX_NOTES_LENGTH = 2000

REQUIRED_FIELDS = ("name", "animal_type")

STRING_FIELDS = {
    "name": MAX_NAME_LENGTH,
    "animal_type": MAX_ANIMAL_TYPE_LENGTH,
    "breed": MAX_BREED_LENGTH,
    "gender": MAX_GENDER_LENGTH,
    "color": MAX_COLOR_LENGTH,
    "health_status": MAX_HEALTH_STATUS_LENGTH,
}

NUMERIC_FIELDS = ("age", "weight")

# Fields the client is allowed to submit (id/timestamps are server-managed)
ALLOWED_FIELDS = {
    "name",
    "animal_type",
    "breed",
    "gender",
    "age",
    "weight",
    "color",
    "health_status",
    "notes",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_animal_data(data: dict, *, partial: bool = False) -> list[str]:
    """Validate an animal data dictionary.

    Parameters
    ----------
    data : dict
        The incoming payload to validate.
    partial : bool
        When *True* (e.g. for PATCH/update requests), required-field checks
        are skipped — only fields actually present in *data* are validated.

    Returns
    -------
    list[str]
        A list of error messages.  Empty list == data is valid.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    # --- Required field checks (skipped in partial mode) -------------------
    if not partial:
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
            if field in REQUIRED_FIELDS and not partial:
                errors.append(f"'{field}' must not be null.")
            continue

        # String fields
        if field in STRING_FIELDS:
            if not isinstance(value, str):
                errors.append(f"'{field}' must be a string.")
                continue
            if not value.strip():
                if field in REQUIRED_FIELDS and not partial:
                    errors.append(f"'{field}' must not be empty.")
                continue
            max_len = STRING_FIELDS[field]
            if len(value) > max_len:
                errors.append(
                    f"'{field}' must be at most {max_len} characters long."
                )

        # Numeric fields
        elif field in NUMERIC_FIELDS:
            if not isinstance(value, (int, float)):
                errors.append(f"'{field}' must be a number.")
                continue
            if field == "age" and value < 0:
                errors.append("'age' must not be negative.")
            if field == "weight" and value <= 0:
                errors.append("'weight' must be greater than zero.")

        # Notes (text)
        elif field == "notes":
            if not isinstance(value, str):
                errors.append("'notes' must be a string.")
            elif len(value) > MAX_NOTES_LENGTH:
                errors.append(
                    f"'notes' must be at most {MAX_NOTES_LENGTH} characters long."
                )

    return errors

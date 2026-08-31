"""
Health-assessment data validation — standalone, reusable by any route or
service layer.

Validates plain dictionaries (e.g. parsed JSON request bodies) against the
rules defined for the HealthAssessment model.  Returns a list of human-
readable error strings; an empty list means the data is valid.

Usage:
    errors = validate_assessment_data(data, animal_repo=repo)
    if errors:
        # return 400 with errors
"""

from app.repositories.base import AnimalRepository

# ---------------------------------------------------------------------------
# Field constraints
# ---------------------------------------------------------------------------

MAX_SYMPTOMS_LENGTH = 5000
ALLOWED_STATUSES = ("pending", "completed", "failed")

REQUIRED_FIELDS = ("symptoms", "animal_id")

# Fields the caller is allowed to submit (id/timestamps are server-managed)
ALLOWED_FIELDS = {
    "animal_id",
    "symptoms",
    "image_ids",
    "diagnosis_result",
    "status",
    "is_red_flag",
    "red_flag_reasons",
}


# ---------------------------------------------------------------------------
# Public API, for health assessment data validation and image upload
# ---------------------------------------------------------------------------


def validate_assessment_data(
    data: dict,
    *,
    animal_repo: AnimalRepository | None = None,
    partial: bool = False,
) -> list[str]:
    """Validate a health-assessment data dictionary.

    Parameters
    ----------
    data : dict
        The incoming payload to validate.
    animal_repo : AnimalRepository, optional
        When provided, ``animal_id`` is checked for existence against this
        repository.  When *None*, only format checks are performed.
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

    # --- Required field checks (skipped in partial mode) ------------------
    if not partial:
        for field in REQUIRED_FIELDS:
            if field not in data or data[field] is None:
                errors.append(f"'{field}' is required.")

    # --- Unknown field check ---------------------------------------------
    for field in data:
        if field not in ALLOWED_FIELDS:
            errors.append(f"Unknown field '{field}'.")

    # --- symptoms ---------------------------------------------------------
    symptoms = data.get("symptoms")
    if symptoms is not None:
        if not isinstance(symptoms, str):
            errors.append("'symptoms' must be a string.")
        elif not symptoms.strip():
            if not partial:
                errors.append("'symptoms' must not be empty.")
        elif len(symptoms) > MAX_SYMPTOMS_LENGTH:
            errors.append(
                f"'symptoms' must be at most {MAX_SYMPTOMS_LENGTH} characters long."
            )

    # --- animal_id --------------------------------------------------------
    animal_id = data.get("animal_id")
    if animal_id is not None:
        if not isinstance(animal_id, str) or not animal_id.strip():
            errors.append("'animal_id' must be a non-empty string.")
        elif animal_repo is not None:
            # Verify the animal actually exists
            if animal_repo.get_by_id(animal_id) is None:
                errors.append(
                    f"'animal_id' does not reference an existing animal ({animal_id})."
                )

    # --- image_ids --------------------------------------------------------
    image_ids = data.get("image_ids")
    if image_ids is not None:
        if not isinstance(image_ids, list):
            errors.append("'image_ids' must be a list.")
        else:
            for idx, item in enumerate(image_ids):
                if not isinstance(item, str):
                    errors.append(
                        f"'image_ids[{idx}]' must be a string."
                    )

    # --- diagnosis_result -------------------------------------------------
    diagnosis_result = data.get("diagnosis_result")
    if diagnosis_result is not None:
        if not isinstance(diagnosis_result, dict):
            errors.append("'diagnosis_result' must be an object/dict or null.")

    # --- status -----------------------------------------------------------
    status = data.get("status")
    if status is not None:
        if not isinstance(status, str):
            errors.append("'status' must be a string.")
        elif status not in ALLOWED_STATUSES:
            errors.append(
                f"'status' must be one of: {', '.join(ALLOWED_STATUSES)}."
            )

    # --- is_red_flag ------------------------------------------------------
    is_red_flag = data.get("is_red_flag")
    if is_red_flag is not None:
        if not isinstance(is_red_flag, bool):
            errors.append("'is_red_flag' must be a boolean.")

    # --- red_flag_reasons -------------------------------------------------
    red_flag_reasons = data.get("red_flag_reasons")
    if red_flag_reasons is not None:
        if not isinstance(red_flag_reasons, list):
            errors.append("'red_flag_reasons' must be a list.")
        else:
            for idx, item in enumerate(red_flag_reasons):
                if not isinstance(item, str):
                    errors.append(
                        f"'red_flag_reasons[{idx}]' must be a string."
                    )

    return errors

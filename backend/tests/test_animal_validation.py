"""Tests for animal data validation logic."""

import pytest
from app.services.animal_validation import validate_animal_data


# ---------------------------------------------------------------------------
# Valid data helpers
# ---------------------------------------------------------------------------

def _valid_animal(**overrides):
    """Return a minimal valid animal payload, with optional overrides."""
    base = {
        "name": "Bholu",
        "animal_type": "Cow",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Full-create validation (partial=False)
# ---------------------------------------------------------------------------

class TestFullValidation:
    def test_valid_minimal_payload(self):
        errors = validate_animal_data(_valid_animal())
        assert errors == []

    def test_valid_full_payload(self):
        data = _valid_animal(
            breed="Gir",
            gender="Female",
            age=5,
            weight=320.5,
            color="Brown",
            health_status="Healthy",
            notes="Docile temperament.",
        )
        errors = validate_animal_data(data)
        assert errors == []

    # --- Required fields ---------------------------------------------------

    def test_missing_name(self):
        data = {"animal_type": "Goat"}
        errors = validate_animal_data(data)
        assert any("name" in e for e in errors)

    def test_missing_animal_type(self):
        data = {"name": "Sheru"}
        errors = validate_animal_data(data)
        assert any("animal_type" in e for e in errors)

    def test_empty_name(self):
        errors = validate_animal_data(_valid_animal(name=""))
        assert any("name" in e for e in errors)

    def test_whitespace_only_animal_type(self):
        errors = validate_animal_data(_valid_animal(animal_type="   "))
        assert any("animal_type" in e for e in errors)

    def test_null_name(self):
        errors = validate_animal_data(_valid_animal(name=None))
        assert any("name" in e for e in errors)

    # --- String length limits ----------------------------------------------

    def test_name_too_long(self):
        errors = validate_animal_data(_valid_animal(name="x" * 101))
        assert any("100" in e for e in errors)

    def test_animal_type_too_long(self):
        errors = validate_animal_data(_valid_animal(animal_type="x" * 51))
        assert any("50" in e for e in errors)

    def test_breed_too_long(self):
        errors = validate_animal_data(_valid_animal(breed="x" * 101))
        assert any("100" in e for e in errors)

    def test_gender_too_long(self):
        errors = validate_animal_data(_valid_animal(gender="x" * 21))
        assert any("20" in e for e in errors)

    def test_notes_too_long(self):
        errors = validate_animal_data(_valid_animal(notes="a" * 2001))
        assert any("2000" in e for e in errors)

    # --- Numeric constraints -----------------------------------------------

    def test_negative_age(self):
        errors = validate_animal_data(_valid_animal(age=-1))
        assert any("age" in e for e in errors)

    def test_zero_age_is_valid(self):
        errors = validate_animal_data(_valid_animal(age=0))
        assert errors == []

    def test_zero_weight(self):
        errors = validate_animal_data(_valid_animal(weight=0))
        assert any("weight" in e for e in errors)

    def test_negative_weight(self):
        errors = validate_animal_data(_valid_animal(weight=-5))
        assert any("weight" in e for e in errors)

    def test_positive_weight_is_valid(self):
        errors = validate_animal_data(_valid_animal(weight=0.5))
        assert errors == []

    def test_age_not_a_number(self):
        errors = validate_animal_data(_valid_animal(age="five"))
        assert any("age" in e and "number" in e for e in errors)

    def test_weight_not_a_number(self):
        errors = validate_animal_data(_valid_animal(weight="heavy"))
        assert any("weight" in e and "number" in e for e in errors)

    # --- Type mismatches ---------------------------------------------------

    def test_name_not_a_string(self):
        errors = validate_animal_data(_valid_animal(name=123))
        assert any("name" in e and "string" in e for e in errors)

    def test_notes_not_a_string(self):
        errors = validate_animal_data(_valid_animal(notes=42))
        assert any("notes" in e and "string" in e for e in errors)

    # --- Unknown fields ----------------------------------------------------

    def test_unknown_field(self):
        errors = validate_animal_data(_valid_animal(vaccinated=True))
        assert any("Unknown" in e for e in errors)

    # --- Non-dict input ----------------------------------------------------

    def test_non_dict_input(self):
        errors = validate_animal_data([1, 2, 3])
        assert any("JSON object" in e for e in errors)

    # --- animal_type accepts any string (not an enum) ----------------------

    def test_animal_type_freeform(self):
        """animal_type must accept any non-empty string, not just a fixed list."""
        for animal_type in ["Cow", "Goat", "Buffalo", "Camel", "Yak", "Llama"]:
            errors = validate_animal_data(_valid_animal(animal_type=animal_type))
            assert errors == [], f"Unexpected errors for '{animal_type}': {errors}"

    def test_gender_freeform(self):
        """gender must accept any string, not just a fixed enum."""
        for gender in ["Male", "Female", "Unknown", "Intersex"]:
            errors = validate_animal_data(_valid_animal(gender=gender))
            assert errors == [], f"Unexpected errors for '{gender}': {errors}"

    # --- Optional fields can be omitted or null ----------------------------

    def test_optional_fields_omitted(self):
        errors = validate_animal_data({"name": "Rani", "animal_type": "Buffalo"})
        assert errors == []

    def test_optional_fields_null(self):
        data = _valid_animal(
            breed=None,
            gender=None,
            age=None,
            weight=None,
            color=None,
            health_status=None,
            notes=None,
        )
        errors = validate_animal_data(data)
        assert errors == []


# ---------------------------------------------------------------------------
# Partial / PATCH validation (partial=True)
# ---------------------------------------------------------------------------

class TestPartialValidation:
    def test_partial_allows_missing_required(self):
        errors = validate_animal_data({"breed": "Sahiwal"}, partial=True)
        assert errors == []

    def test_partial_still_validates_values(self):
        errors = validate_animal_data({"age": -3}, partial=True)
        assert any("age" in e for e in errors)

    def test_partial_rejects_unknown_fields(self):
        errors = validate_animal_data({"foo": "bar"}, partial=True)
        assert any("Unknown" in e for e in errors)

    def test_empty_dict_partial(self):
        errors = validate_animal_data({}, partial=True)
        assert errors == []

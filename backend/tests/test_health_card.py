"""
Tests for the animal health card API route.

Covers:
  1. Clean animal — up-to-date reminders, no active warnings
  2. Active red flag / high-urgency assessment
  3. Overdue reminders and overall "attention_needed" status
  4. Most-recent-assessment wins for warnings
  5. No-data cases (no reminders, no assessments)
  6. Cross-user isolation and 404 behavior
  7. 401 without auth
  8. Response envelope shape and field redaction
"""

import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from app import create_app
from app.config import TestingConfig

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

USER_A_ID = 1
USER_A_EMAIL = "owner@example.com"

USER_B_ID = 2
USER_B_EMAIL = "other@example.com"

PAST_DUE_DATE = "2000-01-01"
FUTURE_DUE_DATE = "2999-01-01T10:30:00+00:00"


def _token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, TestingConfig.SECRET_KEY, algorithm="HS256")


def _auth(user_id=USER_A_ID, email=USER_A_EMAIL):
    return {"Authorization": f"Bearer {_token(user_id, email)}"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create a fresh app instance per test."""
    return create_app("testing")


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Seeding helpers — write straight into the in-memory repositories
# ---------------------------------------------------------------------------

def _seed_animal(app, user_id=USER_A_ID, name="Moti"):
    with app.app_context():
        animal = app.animal_service.create(
            {"name": name, "animal_type": "Cow"}, user_id=user_id
        )
        return str(animal["id"])


def _seed_reminder(app, animal_id, due_date, user_id=USER_A_ID,
                   reminder_type="vaccination"):
    with app.app_context():
        reminder = app.reminder_repo.create({
            "user_id": user_id,
            "animal_id": str(animal_id),
            "reminder_type": reminder_type,
            "due_date": due_date,
            "notes": "Booster dose.",
        })
        return str(reminder["id"])


def _seed_assessment(
    app,
    animal_id,
    symptoms="Limping on front left leg.",
    is_red_flag=False,
    urgency_level="medium",
    created_at=None,
):
    with app.app_context():
        assessment = app.health_assessment_repo.create({
            "animal_id": str(animal_id),
            "symptoms": symptoms,
            "image_ids": ["img_001"],
            "status": "completed",
            "diagnosis_result": {
                "possible_conditions": ["Sprain"],
                "explanation": "Visible limp.",
                "confidence_note": "AI-assisted preliminary assessment.",
                "urgency_level": urgency_level,
            },
            "is_red_flag": is_red_flag,
            "red_flag_reasons": ["keyword match"] if is_red_flag else [],
        })
        if created_at is not None:
            # Direct store update is acceptable for in-memory test fixtures.
            app.health_assessment_repo._store[assessment["id"]][
                "created_at"
            ] = created_at
        return str(assessment["id"])


def _get_health_card(client, animal_id, headers):
    return client.get(f"/api/animals/{animal_id}/health-card", headers=headers)


# ---------------------------------------------------------------------------
# 1. Clean animal
# ---------------------------------------------------------------------------

class TestCleanAnimal:
    def test_up_to_date_reminders_and_no_warnings(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, FUTURE_DUE_DATE, reminder_type="vaccination")
        _seed_reminder(app, animal_id, FUTURE_DUE_DATE, reminder_type="deworming")

        resp = _get_health_card(client, animal_id, _auth())
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True

        data = body["data"]
        assert data["animal"]["id"] == animal_id
        assert data["animal"]["name"] == "Moti"
        assert data["animal"]["animal_type"] == "Cow"

        preventive = data["preventive_care"]
        assert preventive["status"] == "up_to_date"
        assert preventive["vaccination"]["status"] == "up_to_date"
        assert preventive["vaccination"]["days_overdue"] is None
        assert preventive["deworming"]["status"] == "up_to_date"
        assert preventive["deworming"]["days_overdue"] is None
        assert preventive["other"] == []

        warnings = data["health_warnings"]
        assert warnings["has_active_warning"] is False
        assert warnings["urgency_level"] is None
        assert warnings["last_assessed_at"] is None


# ---------------------------------------------------------------------------
# 2. Active red flag
# ---------------------------------------------------------------------------

class TestActiveRedFlag:
    def test_red_flag_surfaces_as_warning(self, app, client):
        animal_id = _seed_animal(app)
        _seed_assessment(
            app,
            animal_id,
            symptoms="Severe bleeding from wound.",
            is_red_flag=True,
            urgency_level="high",
        )

        resp = _get_health_card(client, animal_id, _auth())
        assert resp.status_code == 200
        data = resp.get_json()["data"]

        warnings = data["health_warnings"]
        assert warnings["has_active_warning"] is True
        assert warnings["urgency_level"] == "high"
        assert warnings["last_assessed_at"] is not None

    def test_private_fields_are_redacted(self, app, client):
        animal_id = _seed_animal(app)
        _seed_assessment(
            app,
            animal_id,
            symptoms="Severe bleeding from wound.",
            is_red_flag=True,
            urgency_level="high",
        )

        resp = _get_health_card(client, animal_id, _auth())
        raw = resp.get_data(as_text=True)

        assert "Severe bleeding" not in raw
        assert "possible_conditions" not in raw
        assert "explanation" not in raw
        assert "confidence_note" not in raw
        assert "red_flag_reasons" not in raw
        assert "symptoms" not in raw
        assert "notes" not in raw


# ---------------------------------------------------------------------------
# 3. Overdue reminders
# ---------------------------------------------------------------------------

class TestOverdueReminders:
    def test_overdue_vaccination_and_deworming(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, PAST_DUE_DATE, reminder_type="vaccination")
        _seed_reminder(app, animal_id, PAST_DUE_DATE, reminder_type="deworming")

        resp = _get_health_card(client, animal_id, _auth())
        assert resp.status_code == 200
        data = resp.get_json()["data"]

        preventive = data["preventive_care"]
        assert preventive["status"] == "attention_needed"
        assert preventive["vaccination"]["status"] == "overdue"
        assert preventive["vaccination"]["days_overdue"] > 0
        assert preventive["deworming"]["status"] == "overdue"
        assert preventive["deworming"]["days_overdue"] > 0

    def test_other_reminders_are_listed(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(
            app,
            animal_id,
            PAST_DUE_DATE,
            reminder_type="hoof_trimming",
        )

        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        other = data["preventive_care"]["other"]
        assert len(other) == 1
        assert other[0]["reminder_type"] == "hoof_trimming"
        assert other[0]["status"] == "overdue"
        assert other[0]["days_overdue"] > 0


# ---------------------------------------------------------------------------
# 4. Most recent assessment wins
# ---------------------------------------------------------------------------

class TestMostRecentAssessment:
    def test_newer_clean_assessment_overrides_older_red_flag(self, app, client):
        animal_id = _seed_animal(app)
        _seed_assessment(
            app,
            animal_id,
            is_red_flag=True,
            urgency_level="high",
            created_at="2000-01-01T10:00:00+00:00",
        )
        _seed_assessment(
            app,
            animal_id,
            is_red_flag=False,
            urgency_level="low",
            created_at="2025-01-01T10:00:00+00:00",
        )

        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        assert data["health_warnings"]["has_active_warning"] is False
        assert data["health_warnings"]["urgency_level"] == "low"

    def test_newer_red_flag_overrides_older_clean_assessment(self, app, client):
        animal_id = _seed_animal(app)
        _seed_assessment(
            app,
            animal_id,
            is_red_flag=False,
            urgency_level="low",
            created_at="2000-01-01T10:00:00+00:00",
        )
        _seed_assessment(
            app,
            animal_id,
            is_red_flag=True,
            urgency_level="high",
            created_at="2025-01-01T10:00:00+00:00",
        )

        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        assert data["health_warnings"]["has_active_warning"] is True
        assert data["health_warnings"]["urgency_level"] == "high"


# ---------------------------------------------------------------------------
# 5. No data
# ---------------------------------------------------------------------------

class TestNoData:
    def test_no_reminders_means_unknown_status(self, app, client):
        animal_id = _seed_animal(app)

        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        preventive = data["preventive_care"]
        assert preventive["status"] == "unknown"
        assert preventive["vaccination"]["status"] == "not_recorded"
        assert preventive["deworming"]["status"] == "not_recorded"
        assert preventive["other"] == []

    def test_no_assessments_means_no_warnings(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, FUTURE_DUE_DATE)

        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        warnings = data["health_warnings"]
        assert warnings["has_active_warning"] is False
        assert warnings["urgency_level"] is None
        assert warnings["last_assessed_at"] is None


# ---------------------------------------------------------------------------
# 6. Cross-user isolation
# ---------------------------------------------------------------------------

class TestHealthCardIsolation:
    def test_other_users_animal_is_not_found(self, app, client):
        animal_id = _seed_animal(app, user_id=USER_A_ID)
        resp = _get_health_card(client, animal_id, _auth(USER_B_ID, USER_B_EMAIL))
        assert resp.status_code == 404

    def test_other_users_data_never_appears(self, app, client):
        animal_a = _seed_animal(app, user_id=USER_A_ID, name="Moti")
        animal_b = _seed_animal(app, user_id=USER_B_ID, name="Bholu")
        _seed_assessment(app, animal_b, is_red_flag=True, urgency_level="high")
        _seed_reminder(app, animal_b, PAST_DUE_DATE, user_id=USER_B_ID)

        data = _get_health_card(client, animal_a, _auth()).get_json()["data"]
        assert data["preventive_care"]["status"] == "unknown"
        assert data["health_warnings"]["has_active_warning"] is False


# ---------------------------------------------------------------------------
# 7. Not found
# ---------------------------------------------------------------------------

class TestHealthCardNotFound:
    def test_nonexistent_animal(self, app, client):
        resp = _get_health_card(client, "999", _auth())
        assert resp.status_code == 404
        body = resp.get_json()
        assert body["success"] is False

    def test_non_numeric_animal_id(self, app, client):
        resp = _get_health_card(client, "abc", _auth())
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 8. Auth required
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_no_token(self, client):
        resp = client.get("/api/animals/1/health-card")
        assert resp.status_code == 401

    def test_garbage_token(self, client):
        resp = client.get(
            "/api/animals/1/health-card",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert resp.status_code == 401

    def test_empty_bearer(self, client):
        resp = client.get(
            "/api/animals/1/health-card",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 9. Response envelope shape
# ---------------------------------------------------------------------------

class TestResponseEnvelope:
    def test_success_keys(self, app, client):
        animal_id = _seed_animal(app)
        body = _get_health_card(client, animal_id, _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "data"}
        assert body["success"] is True
        assert isinstance(body["message"], str)

    def test_data_keys(self, app, client):
        animal_id = _seed_animal(app)
        data = _get_health_card(client, animal_id, _auth()).get_json()["data"]
        assert set(data.keys()) == {
            "animal", "preventive_care", "health_warnings", "generated_at"
        }
        assert set(data["preventive_care"].keys()) == {
            "status", "vaccination", "deworming", "other"
        }
        assert set(data["preventive_care"]["vaccination"].keys()) == {
            "reminder_type", "status", "due_date", "days_overdue"
        }
        assert set(data["preventive_care"]["deworming"].keys()) == {
            "reminder_type", "status", "due_date", "days_overdue"
        }
        assert set(data["health_warnings"].keys()) == {
            "has_active_warning", "urgency_level", "last_assessed_at"
        }

    def test_error_keys(self, app, client):
        body = _get_health_card(client, "999", _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "error"}
        assert body["success"] is False

    def test_health_card_service_wiring(self, app):
        from app.services.health_card_service import HealthCardService

        assert isinstance(app.health_card_service, HealthCardService)

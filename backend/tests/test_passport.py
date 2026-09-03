"""
Tests for the animal health passport API route.

Covers:
  1. Happy path — animal profile, assessment history, linked vet case
     summaries, and upcoming/past reminders in one response
  2. Empty passport for an animal with no history
  3. Reminders split into upcoming vs past by due date
  4. Cross-animal and cross-user isolation
  5. 404 for missing/unowned animals, 401 without auth
  6. Response envelope shape
"""

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

# Deterministic dates far from "now" so the upcoming/past split never flakes.
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


def _seed_assessment(app, animal_id, symptoms="Limping on front left leg."):
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
                "urgency_level": "medium",
            },
            "is_red_flag": False,
            "red_flag_reasons": [],
        })
        return str(assessment["id"])


def _seed_summary(app, animal_id, assessment_id, user_id=USER_A_ID):
    with app.app_context():
        summary = app.vet_summary_repo.create({
            "user_id": user_id,
            "animal_id": str(animal_id),
            "assessment_id": str(assessment_id),
            "symptoms": "Limping on front left leg.",
            "image_ids": ["img_001"],
            "diagnosis_result": {},
            "status": "completed",
            "is_red_flag": False,
            "red_flag_reasons": [],
            "animal": {"id": str(animal_id), "name": "Moti"},
        })
        return str(summary["id"])


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


def _get_passport(client, animal_id, headers):
    return client.get(f"/api/animals/{animal_id}/passport", headers=headers)


# ---------------------------------------------------------------------------
# 1. Happy path
# ---------------------------------------------------------------------------

class TestPassportHappyPath:
    def test_full_passport(self, app, client):
        animal_id = _seed_animal(app)
        assessment_1 = _seed_assessment(app, animal_id, symptoms="Limping.")
        _seed_assessment(app, animal_id, symptoms="Loss of appetite.")
        _seed_summary(app, animal_id, assessment_1)
        _seed_reminder(app, animal_id, FUTURE_DUE_DATE)
        _seed_reminder(app, animal_id, PAST_DUE_DATE)

        resp = _get_passport(client, animal_id, _auth())
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True

        data = body["data"]

        # Animal profile
        assert str(data["animal"]["id"]) == animal_id
        assert data["animal"]["name"] == "Moti"
        assert data["animal"]["animal_type"] == "Cow"

        # Complete assessment history
        assert len(data["assessments"]) == 2
        symptoms = {a["symptoms"] for a in data["assessments"]}
        assert symptoms == {"Limping.", "Loss of appetite."}
        for assessment in data["assessments"]:
            assert assessment["diagnosis_result"]["urgency_level"] == "medium"
            assert "created_at" in assessment

        # Vet case summaries linked to the assessments
        assert len(data["vet_case_summaries"]) == 1
        assert data["vet_case_summaries"][0]["assessment_id"] == assessment_1

        # Reminders split by due date
        assert len(data["reminders"]["upcoming"]) == 1
        assert data["reminders"]["upcoming"][0]["due_date"] == FUTURE_DUE_DATE
        assert len(data["reminders"]["past"]) == 1
        assert data["reminders"]["past"][0]["due_date"] == PAST_DUE_DATE

    def test_assessment_without_summary_is_omitted(self, app, client):
        animal_id = _seed_animal(app)
        assessment_1 = _seed_assessment(app, animal_id, symptoms="Limping.")
        _seed_assessment(app, animal_id, symptoms="Coughing.")
        _seed_summary(app, animal_id, assessment_1)

        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        assert len(data["assessments"]) == 2
        assert len(data["vet_case_summaries"]) == 1
        assert data["vet_case_summaries"][0]["assessment_id"] == assessment_1

    def test_summary_snapshot_fields(self, app, client):
        animal_id = _seed_animal(app)
        assessment_id = _seed_assessment(app, animal_id)
        _seed_summary(app, animal_id, assessment_id)

        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        summary = data["vet_case_summaries"][0]
        assert summary["animal_id"] == animal_id
        assert summary["assessment_id"] == assessment_id
        assert summary["symptoms"] == "Limping on front left leg."
        assert summary["animal"]["name"] == "Moti"
        assert "created_at" in summary


# ---------------------------------------------------------------------------
# 2. Empty passport
# ---------------------------------------------------------------------------

class TestEmptyPassport:
    def test_animal_with_no_history(self, app, client):
        animal_id = _seed_animal(app)

        resp = _get_passport(client, animal_id, _auth())
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert str(data["animal"]["id"]) == animal_id
        assert data["assessments"] == []
        assert data["vet_case_summaries"] == []
        assert data["reminders"] == {"upcoming": [], "past": []}


# ---------------------------------------------------------------------------
# 3. Upcoming / past reminder split
# ---------------------------------------------------------------------------

class TestReminderSplit:
    def test_multiple_reminders_on_each_side(self, app, client):
        animal_id = _seed_animal(app)
        for due_date in ("2999-01-01", "2999-06-01"):
            _seed_reminder(app, animal_id, due_date)
        for due_date in ("2000-01-01", "2000-06-01"):
            _seed_reminder(app, animal_id, due_date)

        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        assert len(data["reminders"]["upcoming"]) == 2
        assert len(data["reminders"]["past"]) == 2

    def test_date_only_future_due_date_is_upcoming(self, app, client):
        """Date-only strings parse naive; the comparison must not blow up."""
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, "2999-01-01")

        resp = _get_passport(client, animal_id, _auth())
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data["reminders"]["upcoming"]) == 1
        assert data["reminders"]["past"] == []

    def test_aware_datetime_past_due_date_is_past(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, "2000-01-01T10:30:00+00:00")

        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        assert data["reminders"]["upcoming"] == []
        assert len(data["reminders"]["past"]) == 1

    def test_reminder_fields_preserved(self, app, client):
        animal_id = _seed_animal(app)
        _seed_reminder(app, animal_id, FUTURE_DUE_DATE, reminder_type="deworming")

        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        reminder = data["reminders"]["upcoming"][0]
        assert reminder["reminder_type"] == "deworming"
        assert reminder["notes"] == "Booster dose."
        assert str(reminder["animal_id"]) == animal_id
        assert "created_at" in reminder


# ---------------------------------------------------------------------------
# 4. Cross-animal / cross-user isolation
# ---------------------------------------------------------------------------

class TestPassportIsolation:
    def test_other_animals_data_excluded(self, app, client):
        animal_1 = _seed_animal(app, name="Moti")
        animal_2 = _seed_animal(app, name="Bholu")
        assessment_1 = _seed_assessment(app, animal_1, symptoms="Limping.")
        assessment_2 = _seed_assessment(app, animal_2, symptoms="Coughing.")
        _seed_summary(app, animal_1, assessment_1)
        _seed_summary(app, animal_2, assessment_2)
        _seed_reminder(app, animal_1, FUTURE_DUE_DATE)
        _seed_reminder(app, animal_2, FUTURE_DUE_DATE)

        data = _get_passport(client, animal_1, _auth()).get_json()["data"]

        assert str(data["animal"]["id"]) == animal_1
        assert len(data["assessments"]) == 1
        assert str(data["assessments"][0]["id"]) == assessment_1
        assert len(data["vet_case_summaries"]) == 1
        assert data["vet_case_summaries"][0]["assessment_id"] == assessment_1
        assert len(data["reminders"]["upcoming"]) == 1
        assert str(data["reminders"]["upcoming"][0]["animal_id"]) == animal_1
        # assessment_2 belongs to the other animal and must not appear
        all_assessment_ids = {str(a["id"]) for a in data["assessments"]}
        assert assessment_2 not in all_assessment_ids

    def test_other_users_data_excluded(self, app, client):
        animal_a = _seed_animal(app, user_id=USER_A_ID)
        animal_b = _seed_animal(app, user_id=USER_B_ID)
        assessment_b = _seed_assessment(app, animal_b)
        _seed_summary(app, animal_b, assessment_b, user_id=USER_B_ID)
        _seed_reminder(app, animal_b, FUTURE_DUE_DATE, user_id=USER_B_ID)

        data = _get_passport(client, animal_a, _auth()).get_json()["data"]

        assert str(data["animal"]["id"]) == animal_a
        assert data["assessments"] == []
        assert data["vet_case_summaries"] == []
        assert data["reminders"] == {"upcoming": [], "past": []}


# ---------------------------------------------------------------------------
# 5. Not found / ownership
# ---------------------------------------------------------------------------

class TestPassportNotFound:
    def test_nonexistent_animal(self, app, client):
        resp = _get_passport(client, "999", _auth())
        assert resp.status_code == 404
        body = resp.get_json()
        assert body["success"] is False

    def test_non_numeric_animal_id(self, app, client):
        resp = _get_passport(client, "abc", _auth())
        assert resp.status_code == 404

    def test_other_users_animal_hidden(self, app, client):
        animal_id = _seed_animal(app, user_id=USER_A_ID)
        resp = _get_passport(client, animal_id, _auth(USER_B_ID, USER_B_EMAIL))
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 6. Auth required
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_no_token(self, client):
        resp = client.get("/api/animals/1/passport")
        assert resp.status_code == 401

    def test_garbage_token(self, client):
        resp = client.get(
            "/api/animals/1/passport",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert resp.status_code == 401

    def test_empty_bearer(self, client):
        resp = client.get(
            "/api/animals/1/passport",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 7. Response envelope shape
# ---------------------------------------------------------------------------

class TestResponseEnvelope:
    def test_success_keys(self, app, client):
        animal_id = _seed_animal(app)
        body = _get_passport(client, animal_id, _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "data"}
        assert body["success"] is True
        assert isinstance(body["message"], str)

    def test_data_keys(self, app, client):
        animal_id = _seed_animal(app)
        data = _get_passport(client, animal_id, _auth()).get_json()["data"]
        assert set(data.keys()) == {
            "animal", "assessments", "vet_case_summaries", "reminders"
        }
        assert set(data["reminders"].keys()) == {"upcoming", "past"}

    def test_error_keys(self, app, client):
        body = _get_passport(client, "999", _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "error"}
        assert body["success"] is False

    def test_passport_service_wiring(self, app):
        """The passport service must be wired with its four dependencies."""
        from app.services.passport_service import PassportService

        assert isinstance(app.passport_service, PassportService)

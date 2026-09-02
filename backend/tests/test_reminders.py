"""Comprehensive tests for animal health reminder routes."""

import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from app import create_app
from app.config import TestingConfig

# ---------------------------------------------------------------------------
# Shared auth helpers for testing protected routes
# ---------------------------------------------------------------------------

TEST_USER_ID = 1
TEST_USER_EMAIL = "test@example.com"


def _make_test_token(user_id=TEST_USER_ID, email=TEST_USER_EMAIL):
    """Generate a valid JWT using the testing config's SECRET_KEY."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, TestingConfig.SECRET_KEY, algorithm="HS256")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Fresh app per test — each test gets an empty in-memory store."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """Reusable Authorization header with a valid test JWT."""
    return {"Authorization": f"Bearer {_make_test_token()}"}


@pytest.fixture
def other_user_headers():
    return {"Authorization": f"Bearer {_make_test_token(user_id=2)}"}


def _create_animal(client, headers, name="Bholu"):
    """Seed an animal over HTTP and return its id as a string."""
    resp = client.post(
        "/api/animals",
        data=json.dumps({"name": name, "animal_type": "Cow"}),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.get_json()["data"]["id"]


def _post_reminder(client, animal_id, data, content_type="application/json", headers=None):
    return client.post(
        f"/api/animals/{animal_id}/reminders",
        data=json.dumps(data) if content_type == "application/json" else data,
        content_type=content_type,
        headers=headers,
    )


def _get_reminders(client, animal_id, headers=None):
    return client.get(f"/api/animals/{animal_id}/reminders", headers=headers)


def _delete_reminder(client, reminder_id, headers=None):
    return client.delete(f"/api/reminders/{reminder_id}", headers=headers)


def _valid_payload(**overrides):
    base = {"reminder_type": "vaccination", "due_date": "2030-01-15"}
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# POST /api/animals/<animal_id>/reminders  —  Create
# ---------------------------------------------------------------------------

class TestCreateReminder:
    def test_create_valid_minimal(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["id"] == 1
        assert body["data"]["reminder_type"] == "vaccination"
        assert body["data"]["due_date"] == "2030-01-15"
        assert body["data"]["notes"] is None

    def test_create_with_notes(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client,
            animal_id,
            _valid_payload(notes="FMD booster dose"),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["data"]["notes"] == "FMD booster dose"

    def test_create_deworming_type(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client,
            animal_id,
            _valid_payload(reminder_type="deworming"),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["data"]["reminder_type"] == "deworming"

    def test_create_accepts_custom_type(self, client, auth_headers):
        """reminder_type is freeform — must accept any non-empty string."""
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client,
            animal_id,
            _valid_payload(reminder_type="hoof_trimming"),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.get_json()["data"]["reminder_type"] == "hoof_trimming"

    def test_create_accepts_full_iso_datetime(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client,
            animal_id,
            _valid_payload(due_date="2030-01-15T09:30:00"),
            headers=auth_headers,
        )
        assert resp.status_code == 201

    def test_create_auto_increments_id(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(reminder_type="deworming"), headers=auth_headers
        )
        assert resp.get_json()["data"]["id"] == 2

    def test_create_sets_owner_and_animal_server_side(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        reminder = resp.get_json()["data"]
        assert reminder["user_id"] == "1"
        assert reminder["animal_id"] == str(animal_id)

    def test_create_has_timestamps(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        reminder = resp.get_json()["data"]
        assert "created_at" in reminder
        assert "updated_at" in reminder

    # --- Validation failures ---

    def test_create_missing_reminder_type(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, {"due_date": "2030-01-15"}, headers=auth_headers
        )
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert any("reminder_type" in e for e in body["error"])

    def test_create_missing_due_date(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, {"reminder_type": "vaccination"}, headers=auth_headers
        )
        assert resp.status_code == 400
        assert any("due_date" in e for e in resp.get_json()["error"])

    def test_create_missing_both_fields(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, {}, headers=auth_headers)
        assert resp.status_code == 400
        assert len(resp.get_json()["error"]) == 2

    def test_create_empty_reminder_type(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(reminder_type="   "), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_non_string_reminder_type(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(reminder_type=5), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_reminder_type_too_long(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(reminder_type="x" * 51), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_invalid_due_date_format(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(due_date="15-01-2030"), headers=auth_headers
        )
        assert resp.status_code == 400
        assert any("due_date" in e for e in resp.get_json()["error"])

    def test_create_non_string_due_date(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(due_date=20300115), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_rejects_unknown_field(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(colour="red"), headers=auth_headers
        )
        assert resp.status_code == 400
        assert any("colour" in e for e in resp.get_json()["error"])

    def test_create_rejects_client_supplied_user_id(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(user_id=2), headers=auth_headers
        )
        assert resp.status_code == 400
        assert any("user_id" in e for e in resp.get_json()["error"])

    def test_create_rejects_client_supplied_animal_id(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(animal_id=999), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_non_string_notes(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(notes=42), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_notes_too_long(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, _valid_payload(notes="x" * 2001), headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_malformed_json_body(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, "{bad json", headers=auth_headers
        )
        assert resp.status_code == 400

    def test_create_empty_body(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = client.post(
            f"/api/animals/{animal_id}/reminders", headers=auth_headers
        )
        assert resp.status_code == 400

    # --- Animal scoping ---

    def test_create_for_nonexistent_animal(self, client, auth_headers):
        resp = _post_reminder(client, 999, _valid_payload(), headers=auth_headers)
        assert resp.status_code == 404

    def test_create_for_non_numeric_animal_id(self, client, auth_headers):
        resp = _post_reminder(client, "abc", _valid_payload(), headers=auth_headers)
        assert resp.status_code == 404

    def test_create_for_other_users_animal(self, client, auth_headers, other_user_headers):
        animal_id = _create_animal(client, other_user_headers, name="Theirs")
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/animals/<animal_id>/reminders  —  List
# ---------------------------------------------------------------------------

class TestListReminders:
    def test_list_empty(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _get_reminders(client, animal_id, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"] == []

    def test_list_returns_created_reminders(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        _post_reminder(
            client, animal_id, _valid_payload(reminder_type="deworming"), headers=auth_headers
        )
        resp = _get_reminders(client, animal_id, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 2
        assert data[0]["reminder_type"] == "vaccination"
        assert data[1]["reminder_type"] == "deworming"

    def test_list_scoped_to_single_animal(self, client, auth_headers):
        animal_1 = _create_animal(client, auth_headers, name="A1")
        animal_2 = _create_animal(client, auth_headers, name="A2")
        _post_reminder(client, animal_1, _valid_payload(), headers=auth_headers)
        _post_reminder(client, animal_2, _valid_payload(), headers=auth_headers)

        resp = _get_reminders(client, animal_1, headers=auth_headers)
        data = resp.get_json()["data"]
        assert len(data) == 1
        assert data[0]["animal_id"] == str(animal_1)

    def test_list_nonexistent_animal(self, client, auth_headers):
        resp = _get_reminders(client, 999, headers=auth_headers)
        assert resp.status_code == 404

    def test_list_other_users_animal(self, client, auth_headers, other_user_headers):
        animal_id = _create_animal(client, other_user_headers, name="Theirs")
        resp = _get_reminders(client, animal_id, headers=auth_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/reminders/<reminder_id>  —  Delete
# ---------------------------------------------------------------------------

class TestDeleteReminder:
    def test_delete_existing(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        created = _post_reminder(
            client, animal_id, _valid_payload(), headers=auth_headers
        ).get_json()["data"]

        resp = _delete_reminder(client, created["id"], headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

        # Verify it's gone
        reminders = _get_reminders(client, animal_id, headers=auth_headers).get_json()["data"]
        assert reminders == []

    def test_delete_twice_returns_404(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        created = _post_reminder(
            client, animal_id, _valid_payload(), headers=auth_headers
        ).get_json()["data"]

        _delete_reminder(client, created["id"], headers=auth_headers)
        resp = _delete_reminder(client, created["id"], headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent_id(self, client, auth_headers):
        resp = _delete_reminder(client, 999, headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_non_numeric_id(self, client, auth_headers):
        resp = _delete_reminder(client, "abc", headers=auth_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_create_requires_auth(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=None)
        assert resp.status_code == 401

    def test_list_requires_auth(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _get_reminders(client, animal_id, headers=None)
        assert resp.status_code == 401

    def test_delete_requires_auth(self, client):
        resp = _delete_reminder(client, 1, headers=None)
        assert resp.status_code == 401

    def test_empty_token_rejected(self, client):
        resp = client.get(
            "/api/animals/1/reminders", headers={"Authorization": "Bearer "}
        )
        assert resp.status_code == 401

    def test_garbage_token_rejected(self, client):
        resp = client.get(
            "/api/animals/1/reminders", headers={"Authorization": "Bearer not.a.jwt"}
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Ownership isolation
# ---------------------------------------------------------------------------

class TestOwnershipIsolation:
    def test_other_user_cannot_delete_reminder(
        self, client, auth_headers, other_user_headers
    ):
        animal_id = _create_animal(client, auth_headers)
        created = _post_reminder(
            client, animal_id, _valid_payload(), headers=auth_headers
        ).get_json()["data"]

        resp = _delete_reminder(client, created["id"], headers=other_user_headers)
        assert resp.status_code == 404

        # Confirm it still exists for the real owner
        reminders = _get_reminders(client, animal_id, headers=auth_headers).get_json()["data"]
        assert len(reminders) == 1

    def test_users_see_only_their_own_reminders(
        self, client, auth_headers, other_user_headers
    ):
        animal_a = _create_animal(client, auth_headers, name="Mine")
        animal_b = _create_animal(client, other_user_headers, name="Theirs")

        _post_reminder(client, animal_a, _valid_payload(), headers=auth_headers)
        _post_reminder(
            client, animal_b, _valid_payload(), headers=other_user_headers
        )

        mine = _get_reminders(client, animal_a, headers=auth_headers).get_json()["data"]
        theirs = _get_reminders(
            client, animal_b, headers=other_user_headers
        ).get_json()["data"]
        assert len(mine) == 1
        assert len(theirs) == 1
        assert mine[0]["user_id"] == "1"
        assert theirs[0]["user_id"] == "2"


# ---------------------------------------------------------------------------
# Response envelope
# ---------------------------------------------------------------------------

class TestResponseEnvelope:
    def test_success_envelope_shape(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(client, animal_id, _valid_payload(), headers=auth_headers)
        assert set(resp.get_json().keys()) == {"success", "message", "data"}

    def test_error_envelope_shape(self, client, auth_headers):
        animal_id = _create_animal(client, auth_headers)
        resp = _post_reminder(
            client, animal_id, {"due_date": "2030-01-15"}, headers=auth_headers
        )
        assert resp.status_code == 400
        assert set(resp.get_json().keys()) == {"success", "message", "error"}

    def test_wiring_uses_in_memory_repo(self):
        from app.repositories.in_memory_reminders import InMemoryReminderRepository
        from app.services.reminder_service import ReminderService

        app = create_app("testing")
        assert isinstance(app.reminder_repo, InMemoryReminderRepository)
        assert isinstance(app.reminder_service, ReminderService)

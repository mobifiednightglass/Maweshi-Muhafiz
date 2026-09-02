"""Comprehensive tests for Animal CRUD routes."""

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


def _post(client, data, content_type="application/json", headers=None):
    return client.post(
        "/api/animals",
        data=json.dumps(data) if content_type == "application/json" else data,
        content_type=content_type,
        headers=headers,
    )


def _put(client, animal_id, data, headers=None):
    return client.put(
        f"/api/animals/{animal_id}",
        data=json.dumps(data),
        content_type="application/json",
        headers=headers,
    )


def _valid_payload(**overrides):
    base = {"name": "Bholu", "animal_type": "Cow"}
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# POST /api/animals  —  Create
# ---------------------------------------------------------------------------

class TestCreateAnimal:
    def test_create_valid_minimal(self, client, auth_headers):
        resp = _post(client, _valid_payload(), headers=auth_headers)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["id"] == 1
        assert body["data"]["name"] == "Bholu"
        assert body["data"]["animal_type"] == "Cow"

    def test_create_with_full_payload(self, client, auth_headers):
        data = _valid_payload(
            breed="Gir",
            gender="Female",
            age=5,
            weight=320.5,
            color="Brown",
            health_status="Healthy",
            notes="Docile.",
        )
        resp = _post(client, data, headers=auth_headers)
        assert resp.status_code == 201
        animal = resp.get_json()["data"]
        assert animal["breed"] == "Gir"
        assert animal["weight"] == 320.5

    def test_create_with_unusual_animal_type(self, client, auth_headers):
        """animal_type is freeform — must accept any string."""
        resp = _post(client, _valid_payload(animal_type="Alpaca"), headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["animal_type"] == "Alpaca"

    def test_create_auto_increments_id(self, client, auth_headers):
        _post(client, _valid_payload(name="A1"), headers=auth_headers)
        resp = _post(client, _valid_payload(name="A2"), headers=auth_headers)
        assert resp.get_json()["data"]["id"] == 2

    def test_create_has_timestamps(self, client, auth_headers):
        resp = _post(client, _valid_payload(), headers=auth_headers)
        animal = resp.get_json()["data"]
        assert "created_at" in animal
        assert "updated_at" in animal

    # --- Validation failures ---

    def test_create_missing_name(self, client, auth_headers):
        resp = _post(client, {"animal_type": "Goat"}, headers=auth_headers)
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert any("name" in e for e in body["error"])

    def test_create_empty_animal_type(self, client, auth_headers):
        resp = _post(client, _valid_payload(animal_type=""), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_invalid_age_string(self, client, auth_headers):
        resp = _post(client, _valid_payload(age="five"), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_negative_age(self, client, auth_headers):
        resp = _post(client, _valid_payload(age=-3), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_invalid_weight_string(self, client, auth_headers):
        resp = _post(client, _valid_payload(weight="heavy"), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_zero_weight(self, client, auth_headers):
        resp = _post(client, _valid_payload(weight=0), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_negative_weight(self, client, auth_headers):
        resp = _post(client, _valid_payload(weight=-10), headers=auth_headers)
        assert resp.status_code == 400

    def test_create_malformed_json(self, client, auth_headers):
        resp = client.post(
            "/api/animals",
            data="not json{{{",
            content_type="application/json",
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert resp.get_json()["success"] is False

    def test_create_no_body(self, client, auth_headers):
        resp = client.post("/api/animals", headers=auth_headers)
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/animals  —  List
# ---------------------------------------------------------------------------

class TestListAnimals:
    def test_list_empty(self, client, auth_headers):
        resp = client.get("/api/animals", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"] == []

    def test_list_after_creates(self, client, auth_headers):
        _post(client, _valid_payload(name="A1"), headers=auth_headers)
        _post(client, _valid_payload(name="A2"), headers=auth_headers)
        resp = client.get("/api/animals", headers=auth_headers)
        assert len(resp.get_json()["data"]) == 2


# ---------------------------------------------------------------------------
# GET /api/animals/<id>  —  Get one
# ---------------------------------------------------------------------------

class TestGetAnimal:
    def test_get_existing(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = client.get(f"/api/animals/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["id"] == created["id"]

    def test_get_nonexistent(self, client, auth_headers):
        resp = client.get("/api/animals/999", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.get_json()["success"] is False

    def test_get_invalid_id_format(self, client, auth_headers):
        resp = client.get("/api/animals/abc", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_negative_id(self, client, auth_headers):
        resp = client.get("/api/animals/-1", headers=auth_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/animals/<id>  —  Update
# ---------------------------------------------------------------------------

class TestUpdateAnimal:
    def test_update_single_field(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = _put(client, created["id"], {"name": "Updated Name"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["name"] == "Updated Name"
        # animal_type should be unchanged
        assert resp.get_json()["data"]["animal_type"] == "Cow"

    def test_update_refreshes_updated_at(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        updated = _put(client, created["id"], {"name": "New"}, headers=auth_headers).get_json()["data"]
        # updated_at should be >= created_at
        assert updated["updated_at"] >= created["updated_at"]

    def test_update_nonexistent(self, client, auth_headers):
        resp = _put(client, 999, {"name": "Ghost"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_update_invalid_id(self, client, auth_headers):
        resp = _put(client, "xyz", {"name": "Bad"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_update_with_invalid_data(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = _put(client, created["id"], {"age": -5}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_with_negative_weight(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = _put(client, created["id"], {"weight": -1}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_with_zero_weight(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = _put(client, created["id"], {"weight": 0}, headers=auth_headers)
        assert resp.status_code == 400

    def test_update_malformed_json(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = client.put(
            f"/api/animals/{created['id']}",
            data="not-json",
            content_type="application/json",
            headers=auth_headers,
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/animals/<id>  —  Delete
# ---------------------------------------------------------------------------

class TestDeleteAnimal:
    def test_delete_existing(self, client, auth_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = client.delete(f"/api/animals/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True
        # Verify it's gone
        resp = client.get(f"/api/animals/{created['id']}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/api/animals/999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_invalid_id(self, client, auth_headers):
        resp = client.delete("/api/animals/abc", headers=auth_headers)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Response envelope consistency
# ---------------------------------------------------------------------------

class TestResponseEnvelope:
    def test_success_has_expected_keys(self, client, auth_headers):
        resp = _post(client, _valid_payload(), headers=auth_headers)
        body = resp.get_json()
        assert "success" in body
        assert "message" in body
        assert "data" in body

    def test_error_has_expected_keys(self, client, auth_headers):
        resp = client.get("/api/animals/999", headers=auth_headers)
        body = resp.get_json()
        assert "success" in body
        assert "message" in body
        assert "error" in body

    def test_no_raw_exceptions_leaked(self, client, auth_headers):
        """Error responses must never expose traceback or raw exception text."""
        resp = _post(client, {"animal_type": "Goat"}, headers=auth_headers)  # missing name
        body_str = resp.data.decode()
        assert "Traceback" not in body_str
        assert "Exception" not in body_str
# ---------------------------------------------------------------------------
# Ownership isolation between users
# ---------------------------------------------------------------------------

def _make_other_user_token(user_id, email="other@example.com"):
    from datetime import datetime, timedelta, timezone
    import jwt
    from app.config import TestingConfig

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, TestingConfig.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def other_user_headers():
    return {"Authorization": f"Bearer {_make_other_user_token(user_id=2)}"}


class TestOwnershipIsolation:
    def test_create_sets_owner_automatically(self, client, auth_headers):
        animal = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        assert animal["user_id"] == "1"

    def test_client_supplied_user_id_is_rejected(self, client, auth_headers):
        """Client cannot inject a user_id — validation rejects it as an unknown field."""
        resp = _post(client, _valid_payload(user_id="999"), headers=auth_headers)
        assert resp.status_code == 400

    def test_list_only_shows_own_animals(self, client, auth_headers, other_user_headers):
        _post(client, _valid_payload(name="Mine"), headers=auth_headers)
        _post(client, _valid_payload(name="TheirsA"), headers=other_user_headers)
        _post(client, _valid_payload(name="TheirsB"), headers=other_user_headers)

        my_list = client.get("/api/animals", headers=auth_headers).get_json()["data"]
        their_list = client.get("/api/animals", headers=other_user_headers).get_json()["data"]

        assert len(my_list) == 1
        assert len(their_list) == 2

    def test_cannot_get_others_animal(self, client, auth_headers, other_user_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = client.get(f"/api/animals/{created['id']}", headers=other_user_headers)
        assert resp.status_code == 404

    def test_cannot_update_others_animal(self, client, auth_headers, other_user_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = _put(client, created["id"], {"name": "Hacked"}, headers=other_user_headers)
        assert resp.status_code == 404

    def test_cannot_delete_others_animal(self, client, auth_headers, other_user_headers):
        created = _post(client, _valid_payload(), headers=auth_headers).get_json()["data"]
        resp = client.delete(f"/api/animals/{created['id']}", headers=other_user_headers)
        assert resp.status_code == 404
        # Confirm it still exists for the real owner
        still_there = client.get(f"/api/animals/{created['id']}", headers=auth_headers)
        assert still_there.status_code == 200


# ---------------------------------------------------------------------------
# Region field (optional; feeds the regional insights endpoint)
# ---------------------------------------------------------------------------

class TestRegionField:
    def test_create_with_region(self, client, auth_headers):
        resp = _post(client, _valid_payload(region="Punjab"), headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["region"] == "Punjab"

    def test_create_without_region_defaults_to_none(self, client, auth_headers):
        resp = _post(client, _valid_payload(), headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["region"] is None

    def test_create_with_null_region(self, client, auth_headers):
        resp = _post(client, _valid_payload(region=None), headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()["data"]["region"] is None

    def test_create_region_at_max_length(self, client, auth_headers):
        resp = _post(client, _valid_payload(region="r" * 100), headers=auth_headers)
        assert resp.status_code == 201

    def test_create_region_too_long(self, client, auth_headers):
        resp = _post(client, _valid_payload(region="r" * 101), headers=auth_headers)
        assert resp.status_code == 400
        assert any("region" in e for e in resp.get_json()["error"])

    def test_create_region_must_be_string(self, client, auth_headers):
        resp = _post(client, _valid_payload(region=42), headers=auth_headers)
        assert resp.status_code == 400
        assert any("region" in e for e in resp.get_json()["error"])

    def test_update_region(self, client, auth_headers):
        created = (
            _post(client, _valid_payload(region="Punjab"), headers=auth_headers)
            .get_json()["data"]
        )
        resp = _put(client, created["id"], {"region": "Sindh"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["region"] == "Sindh"

    def test_update_can_clear_region(self, client, auth_headers):
        created = (
            _post(client, _valid_payload(region="Punjab"), headers=auth_headers)
            .get_json()["data"]
        )
        resp = _put(client, created["id"], {"region": None}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["region"] is None
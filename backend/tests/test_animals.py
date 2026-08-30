"""Comprehensive tests for Animal CRUD routes."""

import json

import pytest
from app import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Fresh app per test — each test gets an empty in-memory store."""
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def _post(client, data, content_type="application/json"):
    return client.post(
        "/api/animals",
        data=json.dumps(data) if content_type == "application/json" else data,
        content_type=content_type,
    )


def _put(client, animal_id, data):
    return client.put(
        f"/api/animals/{animal_id}",
        data=json.dumps(data),
        content_type="application/json",
    )


def _valid_payload(**overrides):
    base = {"name": "Bholu", "animal_type": "Cow"}
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# POST /api/animals  —  Create
# ---------------------------------------------------------------------------

class TestCreateAnimal:
    def test_create_valid_minimal(self, client):
        resp = _post(client, _valid_payload())
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["id"] == 1
        assert body["data"]["name"] == "Bholu"
        assert body["data"]["animal_type"] == "Cow"

    def test_create_with_full_payload(self, client):
        data = _valid_payload(
            breed="Gir",
            gender="Female",
            age=5,
            weight=320.5,
            color="Brown",
            health_status="Healthy",
            notes="Docile.",
        )
        resp = _post(client, data)
        assert resp.status_code == 201
        animal = resp.get_json()["data"]
        assert animal["breed"] == "Gir"
        assert animal["weight"] == 320.5

    def test_create_with_unusual_animal_type(self, client):
        """animal_type is freeform — must accept any string."""
        resp = _post(client, _valid_payload(animal_type="Alpaca"))
        assert resp.status_code == 201
        assert resp.get_json()["data"]["animal_type"] == "Alpaca"

    def test_create_auto_increments_id(self, client):
        _post(client, _valid_payload(name="A1"))
        resp = _post(client, _valid_payload(name="A2"))
        assert resp.get_json()["data"]["id"] == 2

    def test_create_has_timestamps(self, client):
        resp = _post(client, _valid_payload())
        animal = resp.get_json()["data"]
        assert "created_at" in animal
        assert "updated_at" in animal

    # --- Validation failures ---

    def test_create_missing_name(self, client):
        resp = _post(client, {"animal_type": "Goat"})
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert any("name" in e for e in body["error"])

    def test_create_empty_animal_type(self, client):
        resp = _post(client, _valid_payload(animal_type=""))
        assert resp.status_code == 400

    def test_create_invalid_age_string(self, client):
        resp = _post(client, _valid_payload(age="five"))
        assert resp.status_code == 400

    def test_create_negative_age(self, client):
        resp = _post(client, _valid_payload(age=-3))
        assert resp.status_code == 400

    def test_create_invalid_weight_string(self, client):
        resp = _post(client, _valid_payload(weight="heavy"))
        assert resp.status_code == 400

    def test_create_zero_weight(self, client):
        resp = _post(client, _valid_payload(weight=0))
        assert resp.status_code == 400

    def test_create_negative_weight(self, client):
        resp = _post(client, _valid_payload(weight=-10))
        assert resp.status_code == 400

    def test_create_malformed_json(self, client):
        resp = client.post(
            "/api/animals",
            data="not json{{{",
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.get_json()["success"] is False

    def test_create_no_body(self, client):
        resp = client.post("/api/animals")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/animals  —  List
# ---------------------------------------------------------------------------

class TestListAnimals:
    def test_list_empty(self, client):
        resp = client.get("/api/animals")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"] == []

    def test_list_after_creates(self, client):
        _post(client, _valid_payload(name="A1"))
        _post(client, _valid_payload(name="A2"))
        resp = client.get("/api/animals")
        assert len(resp.get_json()["data"]) == 2


# ---------------------------------------------------------------------------
# GET /api/animals/<id>  —  Get one
# ---------------------------------------------------------------------------

class TestGetAnimal:
    def test_get_existing(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = client.get(f"/api/animals/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["id"] == created["id"]

    def test_get_nonexistent(self, client):
        resp = client.get("/api/animals/999")
        assert resp.status_code == 404
        assert resp.get_json()["success"] is False

    def test_get_invalid_id_format(self, client):
        resp = client.get("/api/animals/abc")
        assert resp.status_code == 404

    def test_get_negative_id(self, client):
        resp = client.get("/api/animals/-1")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PUT /api/animals/<id>  —  Update
# ---------------------------------------------------------------------------

class TestUpdateAnimal:
    def test_update_single_field(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = _put(client, created["id"], {"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["name"] == "Updated Name"
        # animal_type should be unchanged
        assert resp.get_json()["data"]["animal_type"] == "Cow"

    def test_update_refreshes_updated_at(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        updated = _put(client, created["id"], {"name": "New"}).get_json()["data"]
        # updated_at should be >= created_at
        assert updated["updated_at"] >= created["updated_at"]

    def test_update_nonexistent(self, client):
        resp = _put(client, 999, {"name": "Ghost"})
        assert resp.status_code == 404

    def test_update_invalid_id(self, client):
        resp = _put(client, "xyz", {"name": "Bad"})
        assert resp.status_code == 404

    def test_update_with_invalid_data(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = _put(client, created["id"], {"age": -5})
        assert resp.status_code == 400

    def test_update_with_negative_weight(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = _put(client, created["id"], {"weight": -1})
        assert resp.status_code == 400

    def test_update_with_zero_weight(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = _put(client, created["id"], {"weight": 0})
        assert resp.status_code == 400

    def test_update_malformed_json(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = client.put(
            f"/api/animals/{created['id']}",
            data="not-json",
            content_type="application/json",
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/animals/<id>  —  Delete
# ---------------------------------------------------------------------------

class TestDeleteAnimal:
    def test_delete_existing(self, client):
        created = _post(client, _valid_payload()).get_json()["data"]
        resp = client.delete(f"/api/animals/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True
        # Verify it's gone
        resp = client.get(f"/api/animals/{created['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/animals/999")
        assert resp.status_code == 404

    def test_delete_invalid_id(self, client):
        resp = client.delete("/api/animals/abc")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Response envelope consistency
# ---------------------------------------------------------------------------

class TestResponseEnvelope:
    def test_success_has_expected_keys(self, client):
        resp = _post(client, _valid_payload())
        body = resp.get_json()
        assert "success" in body
        assert "message" in body
        assert "data" in body

    def test_error_has_expected_keys(self, client):
        resp = client.get("/api/animals/999")
        body = resp.get_json()
        assert "success" in body
        assert "message" in body
        assert "error" in body

    def test_no_raw_exceptions_leaked(self, client):
        """Error responses must never expose traceback or raw exception text."""
        resp = _post(client, {"animal_type": "Goat"})  # missing name
        body_str = resp.data.decode()
        assert "Traceback" not in body_str
        assert "Exception" not in body_str

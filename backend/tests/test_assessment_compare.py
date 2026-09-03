"""
Tests for the assessment comparison route.

Endpoint: GET /api/animals/<animal_id>/assessments/compare
          ?assessment_id_1=...&assessment_id_2=...

Covers:
  1. Happy path — both assessments returned in full, keyed by param order
  2. Missing/blank query parameters → 400
  3. Missing, invalid, or foreign assessments → 404
  4. Ownership isolation across users and animals
  5. Auth required, envelope shape
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


def _seed_assessment(app, animal_id, symptoms="Limping.", image_ids=None):
    with app.app_context():
        assessment = app.health_assessment_repo.create({
            "animal_id": str(animal_id),
            "symptoms": symptoms,
            "image_ids": image_ids if image_ids is not None else ["img_001"],
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


def _compare(client, animal_id, id_1, id_2, headers):
    return client.get(
        f"/api/animals/{animal_id}/assessments/compare"
        f"?assessment_id_1={id_1}&assessment_id_2={id_2}",
        headers=headers,
    )


# ---------------------------------------------------------------------------
# 1. Happy path
# ---------------------------------------------------------------------------

class TestCompareHappyPath:
    def test_compare_two_assessments(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id, symptoms="Limping badly.")
        second = _seed_assessment(app, animal_id, symptoms="Limp improved.")

        resp = _compare(client, animal_id, first, second, _auth())
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True

        data = body["data"]
        assert set(data.keys()) == {"assessment_1", "assessment_2"}
        assert str(data["assessment_1"]["id"]) == first
        assert str(data["assessment_2"]["id"]) == second

    def test_full_assessment_data_returned(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(
            app, animal_id, symptoms="Before symptoms.", image_ids=["img_before"],
        )
        second = _seed_assessment(
            app, animal_id, symptoms="After symptoms.", image_ids=["img_after"],
        )

        data = _compare(client, animal_id, first, second, _auth()).get_json()["data"]

        for key, symptoms, image_ids in (
            ("assessment_1", "Before symptoms.", ["img_before"]),
            ("assessment_2", "After symptoms.", ["img_after"]),
        ):
            record = data[key]
            assert record["symptoms"] == symptoms
            assert record["image_ids"] == image_ids
            assert record["diagnosis_result"]["urgency_level"] == "medium"
            assert record["status"] == "completed"
            assert record["is_red_flag"] is False
            assert "created_at" in record
            assert "updated_at" in record
            assert str(record["animal_id"]) == animal_id

    def test_param_order_preserved(self, app, client):
        """assessment_1 is whichever id was passed as assessment_id_1."""
        animal_id = _seed_animal(app)
        earlier = _seed_assessment(app, animal_id, symptoms="Earlier.")
        later = _seed_assessment(app, animal_id, symptoms="Later.")

        data = (
            _compare(client, animal_id, later, earlier, _auth())
            .get_json()["data"]
        )
        assert str(data["assessment_1"]["id"]) == later
        assert str(data["assessment_2"]["id"]) == earlier

    def test_same_assessment_twice_is_allowed(self, app, client):
        animal_id = _seed_animal(app)
        only = _seed_assessment(app, animal_id)

        resp = _compare(client, animal_id, only, only, _auth())
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert str(data["assessment_1"]["id"]) == only
        assert str(data["assessment_2"]["id"]) == only

    def test_comparison_between_statuses(self, app, client):
        animal_id = _seed_animal(app)
        pending = _seed_assessment(app, animal_id, symptoms="Pending.")
        with app.app_context():
            app.health_assessment_repo.update(pending, {"status": "pending"})
        completed = _seed_assessment(app, animal_id, symptoms="Completed.")

        data = _compare(client, animal_id, pending, completed, _auth()).get_json()["data"]
        assert data["assessment_1"]["status"] == "pending"
        assert data["assessment_2"]["status"] == "completed"


# ---------------------------------------------------------------------------
# 2. Query-parameter validation → 400
# ---------------------------------------------------------------------------

class TestCompareValidation:
    def test_missing_first_param(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = client.get(
            f"/api/animals/{animal_id}/assessments/compare"
            f"?assessment_id_2={second}",
            headers=_auth(),
        )
        assert resp.status_code == 400
        assert resp.get_json()["success"] is False

    def test_missing_second_param(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = client.get(
            f"/api/animals/{animal_id}/assessments/compare"
            f"?assessment_id_1={first}",
            headers=_auth(),
        )
        assert resp.status_code == 400

    def test_missing_both_params(self, app, client):
        animal_id = _seed_animal(app)

        resp = client.get(
            f"/api/animals/{animal_id}/assessments/compare",
            headers=_auth(),
        )
        assert resp.status_code == 400

    def test_blank_param_values(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = client.get(
            f"/api/animals/{animal_id}/assessments/compare"
            f"?assessment_id_1=%20&assessment_id_2={second}",
            headers=_auth(),
        )
        assert resp.status_code == 400

    def test_param_validation_preceded_by_animal_check(self, app, client):
        """Missing params on a nonexistent animal → 404 (animal checked first)."""
        resp = client.get(
            "/api/animals/999/assessments/compare",
            headers=_auth(),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. Not found → 404
# ---------------------------------------------------------------------------

class TestCompareNotFound:
    def test_nonexistent_animal(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = _compare(client, "999", first, second, _auth())
        assert resp.status_code == 404
        assert resp.get_json()["success"] is False

    def test_non_numeric_animal_id(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = _compare(client, "abc", first, second, _auth())
        assert resp.status_code == 404

    def test_nonexistent_first_assessment(self, app, client):
        animal_id = _seed_animal(app)
        second = _seed_assessment(app, animal_id)

        resp = _compare(client, animal_id, "999", second, _auth())
        assert resp.status_code == 404

    def test_nonexistent_second_assessment(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)

        resp = _compare(client, animal_id, first, "999", _auth())
        assert resp.status_code == 404

    def test_non_numeric_assessment_id(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)

        resp = _compare(client, animal_id, first, "not-an-id", _auth())
        assert resp.status_code == 404

    def test_assessment_from_another_animal_same_user(self, app, client):
        """An assessment of a different animal cannot be compared here."""
        animal_a = _seed_animal(app, name="Moti")
        animal_b = _seed_animal(app, name="Bholu")
        on_a = _seed_assessment(app, animal_a)
        on_b = _seed_assessment(app, animal_b)

        resp = _compare(client, animal_a, on_a, on_b, _auth())
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 4. Ownership isolation
# ---------------------------------------------------------------------------

class TestCompareOwnership:
    def test_other_users_animal_hidden(self, app, client):
        animal_id = _seed_animal(app, user_id=USER_A_ID)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        resp = _compare(
            client, animal_id, first, second,
            _auth(USER_B_ID, USER_B_EMAIL),
        )
        assert resp.status_code == 404

    def test_other_users_assessment_hidden(self, app, client):
        """User B cannot pull user A's assessment into their own comparison."""
        mine = _seed_animal(app, user_id=USER_A_ID, name="Mine")
        theirs = _seed_animal(app, user_id=USER_B_ID, name="Theirs")
        my_assessment = _seed_assessment(app, mine)
        their_assessment = _seed_assessment(app, theirs)
        their_other = _seed_assessment(app, theirs)

        # User B tries to compare their own assessment with user A's
        resp = _compare(
            client, theirs, their_assessment, my_assessment,
            _auth(USER_B_ID, USER_B_EMAIL),
        )
        assert resp.status_code == 404

        # Sanity: user B comparing two of their own still works
        ok = _compare(
            client, theirs, their_assessment, their_other,
            _auth(USER_B_ID, USER_B_EMAIL),
        )
        assert ok.status_code == 200


# ---------------------------------------------------------------------------
# 5. Auth and envelope
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_no_token(self, client):
        resp = client.get("/api/animals/1/assessments/compare")
        assert resp.status_code == 401

    def test_garbage_token(self, client):
        resp = client.get(
            "/api/animals/1/assessments/compare",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert resp.status_code == 401

    def test_empty_bearer(self, client):
        resp = client.get(
            "/api/animals/1/assessments/compare",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401


class TestResponseEnvelope:
    def test_success_keys(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)
        second = _seed_assessment(app, animal_id)

        body = _compare(client, animal_id, first, second, _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "data"}
        assert body["success"] is True
        assert isinstance(body["message"], str)

    def test_error_keys(self, app, client):
        animal_id = _seed_animal(app)
        first = _seed_assessment(app, animal_id)

        body = _compare(client, animal_id, first, "999", _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "error"}
        assert body["success"] is False

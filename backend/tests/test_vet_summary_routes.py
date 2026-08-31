"""
Tests for Vet-Ready Case Summary API routes.

Covers:
  1. Owner can create and retrieve a summary
  2. Summary contains correct user_id, animal_id, assessment_id
  3. Another user cannot access it
  4. Duplicate creation does not create another summary
  5. Missing resources return 404
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
    application = create_app("testing")
    return application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


def _seed_animal_and_assessment(app, animal_id="animal_1", user_id=USER_A_ID):
    """Seed an animal and a completed assessment directly into the repos.

    Returns the assessment record dict.
    """
    with app.app_context():
        # Create an animal owned by user_id with all snapshot fields
        animal = app.animal_service.create(
            {
                "name": "Moti",
                "animal_type": "Cow",
                "breed": "Sahiwal",
                "gender": "Female",
                "age": 5,
                "weight": 350.0,
                "color": "Brown",
                "health_status": "healthy",
            },
            user_id=user_id,
        )
        aid = animal["id"]

        # Create a completed assessment for this animal
        assessment = app.health_assessment_repo.create({
            "animal_id": str(aid),
            "symptoms": "Limping on front left leg.",
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
        return str(aid), str(assessment["id"])


# ---------------------------------------------------------------------------
# 1. Owner can create and retrieve a summary
# ---------------------------------------------------------------------------

class TestOwnerCreateAndRetrieve:
    def test_create_summary(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["success"] is True
        assert "id" in body["data"]

    def test_get_summary_after_create(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)

        # Create first
        client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )

        # Then retrieve
        resp = client.get(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["data"]["assessment_id"] == assess_id

    def test_get_without_create_returns_404(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.get(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 2. Summary contains correct user_id, animal_id, assessment_id
# ---------------------------------------------------------------------------

class TestSummaryFields:
    def test_correct_ids_in_response(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        data = resp.get_json()["data"]
        assert str(data["user_id"]) == str(USER_A_ID)
        assert str(data["animal_id"]) == str(aid)
        assert str(data["assessment_id"]) == str(assess_id)

    def test_assessment_data_snapshotted(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        data = resp.get_json()["data"]
        assert data["symptoms"] == "Limping on front left leg."
        assert data["diagnosis_result"]["possible_conditions"] == ["Sprain"]
        assert data["status"] == "completed"


# ---------------------------------------------------------------------------
# 3. Another user cannot access it
# ---------------------------------------------------------------------------

class TestOwnershipIsolation:
    def test_other_user_cannot_create_summary(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app, user_id=USER_A_ID)

        # User B tries to create a summary for User A's animal
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(USER_B_ID, USER_B_EMAIL),
        )
        assert resp.status_code == 404

    def test_other_user_cannot_get_summary(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app, user_id=USER_A_ID)

        # Owner creates the summary
        client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )

        # User B tries to retrieve it
        resp = client.get(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(USER_B_ID, USER_B_EMAIL),
        )
        assert resp.status_code == 404

    def test_no_auth_returns_401(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. Duplicate creation does not create another summary
# ---------------------------------------------------------------------------

class TestIdempotentCreation:
    def test_duplicate_post_returns_existing(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        url = f"/api/animals/{aid}/assessments/{assess_id}/summary"

        # First creation
        resp1 = client.post(url, headers=_auth())
        assert resp1.status_code == 201
        id1 = resp1.get_json()["data"]["id"]

        # Second creation — should return existing, not create a duplicate
        resp2 = client.post(url, headers=_auth())
        assert resp2.status_code == 200
        id2 = resp2.get_json()["data"]["id"]

        assert id1 == id2

    def test_only_one_summary_in_repo(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        url = f"/api/animals/{aid}/assessments/{assess_id}/summary"

        client.post(url, headers=_auth())
        client.post(url, headers=_auth())

        with app.app_context():
            summaries = app.vet_summary_repo.get_by_user_id(USER_A_ID)
            assert len(summaries) == 1


# ---------------------------------------------------------------------------
# 5. Missing resources return 404
# ---------------------------------------------------------------------------

class TestMissingResources:
    def test_nonexistent_animal_returns_404(self, app, client):
        resp = client.post(
            "/api/animals/no_such/assessments/1/summary",
            headers=_auth(),
        )
        assert resp.status_code == 404

    def test_nonexistent_assessment_returns_404(self, app, client):
        aid, _ = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/99999/summary",
            headers=_auth(),
        )
        assert resp.status_code == 404

    def test_assessment_belongs_to_different_animal_returns_404(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        # Use a different animal_id in the URL but the real assessment_id
        resp = client.post(
            f"/api/animals/wrong_animal/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 6. Animal snapshot in summary
# ---------------------------------------------------------------------------

_ANIMAL_SNAPSHOT_FIELDS = (
    "id", "name", "animal_type", "breed", "gender",
    "age", "weight", "color", "health_status",
)


class TestAnimalSnapshot:
    def test_create_response_contains_animal(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        data = resp.get_json()["data"]
        assert "animal" in data
        assert data["animal"] is not None

    def test_animal_has_exactly_snapshot_fields(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        animal = resp.get_json()["data"]["animal"]
        assert set(animal.keys()) == set(_ANIMAL_SNAPSHOT_FIELDS)

    def test_animal_snapshot_values(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        animal = resp.get_json()["data"]["animal"]
        assert animal["name"] == "Moti"
        assert animal["animal_type"] == "Cow"
        assert animal["breed"] == "Sahiwal"
        assert animal["gender"] == "Female"
        assert animal["age"] == 5
        assert animal["weight"] == 350.0
        assert animal["color"] == "Brown"
        assert animal["health_status"] == "healthy"

    def test_get_response_contains_animal(self, app, client):
        aid, assess_id = _seed_animal_and_assessment(app)
        # Create first
        client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        # Then retrieve
        resp = client.get(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        data = resp.get_json()["data"]
        assert "animal" in data
        assert data["animal"]["name"] == "Moti"
        assert set(data["animal"].keys()) == set(_ANIMAL_SNAPSHOT_FIELDS)

    def test_animal_belongs_to_authenticated_user(self, app, client):
        """Animal snapshot must come from the authenticated user's animal,
        not from any client-supplied user_id."""
        aid, assess_id = _seed_animal_and_assessment(app, user_id=USER_A_ID)

        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(USER_A_ID, USER_A_EMAIL),
        )
        animal = resp.get_json()["data"]["animal"]
        # The animal should have the correct name from the seeded data
        assert animal["name"] == "Moti"
        # The animal id should match the animal used in the URL
        assert str(animal["id"]) == str(aid)

    def test_no_extra_animal_fields_leaked(self, app, client):
        """Ensure internal fields like user_id or notes are NOT in the snapshot."""
        aid, assess_id = _seed_animal_and_assessment(app)
        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        animal = resp.get_json()["data"]["animal"]
        for forbidden in ("user_id", "notes", "created_at", "updated_at"):
            assert forbidden not in animal


# ---------------------------------------------------------------------------
# 7. Animal backfill on stale summaries (created before snapshot feature)
# ---------------------------------------------------------------------------

class TestAnimalBackfill:
    """Regression: POST must populate animal on an existing summary that has
    animal=null, without creating a duplicate."""

    def _seed_stale_summary(self, app, user_id=USER_A_ID):
        """Create a summary with animal=None, simulating a pre-feature record."""
        aid, assess_id = _seed_animal_and_assessment(app, user_id=user_id)
        with app.app_context():
            app.vet_summary_repo.create({
                "user_id": user_id,
                "animal_id": aid,
                "assessment_id": assess_id,
                "symptoms": "Limping on front left leg.",
                "image_ids": ["img_001"],
                "diagnosis_result": {"possible_conditions": ["Sprain"]},
                "status": "completed",
                "is_red_flag": False,
                "red_flag_reasons": [],
                # No animal key at all — repo stores None
            })
        return aid, assess_id

    def test_post_backfills_null_animal(self, app, client):
        aid, assess_id = self._seed_stale_summary(app)

        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["animal"] is not None
        assert data["animal"]["name"] == "Moti"
        assert set(data["animal"].keys()) == set(_ANIMAL_SNAPSHOT_FIELDS)

    def test_get_after_backfill_has_animal(self, app, client):
        aid, assess_id = self._seed_stale_summary(app)

        # POST triggers backfill
        client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )

        # GET should also have the animal
        resp = client.get(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )
        data = resp.get_json()["data"]
        assert data["animal"] is not None
        assert data["animal"]["name"] == "Moti"

    def test_backfill_does_not_create_duplicate(self, app, client):
        aid, assess_id = self._seed_stale_summary(app)

        client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(),
        )

        with app.app_context():
            summaries = app.vet_summary_repo.get_by_user_id(USER_A_ID)
            assert len(summaries) == 1

    def test_backfill_uses_authenticated_user_animal(self, app, client):
        """The backfilled animal must come from g.user_id, not the client."""
        aid, assess_id = self._seed_stale_summary(app, user_id=USER_A_ID)

        resp = client.post(
            f"/api/animals/{aid}/assessments/{assess_id}/summary",
            headers=_auth(USER_A_ID, USER_A_EMAIL),
        )
        animal = resp.get_json()["data"]["animal"]
        assert str(animal["id"]) == str(aid)
        assert animal["name"] == "Moti"

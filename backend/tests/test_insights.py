"""
Tests for the regional insights API route (GET /api/insights/area).

Covers:
  1. Per-region grouping of assessment counts
  2. Flagged/urgent counting (is_red_flag or high urgency)
  3. The "unknown" bucket for animals without a region
  4. User isolation — only the caller's own data is counted
  5. Ordering, envelope shape, and auth
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

def _seed_animal(app, user_id=USER_A_ID, name="Moti", region=None):
    with app.app_context():
        animal = app.animal_service.create(
            {"name": name, "animal_type": "Cow", "region": region},
            user_id=user_id,
        )
        return str(animal["id"])


def _seed_assessment(app, animal_id, *, is_red_flag=False, urgency="medium"):
    with app.app_context():
        assessment = app.health_assessment_repo.create({
            "animal_id": str(animal_id),
            "symptoms": "Limping on front left leg.",
            "image_ids": [],
            "status": "completed",
            "diagnosis_result": {
                "possible_conditions": ["Sprain"],
                "explanation": "Visible limp.",
                "confidence_note": "AI-assisted preliminary assessment.",
                "urgency_level": urgency,
            },
            "is_red_flag": is_red_flag,
            "red_flag_reasons": [],
        })
        return str(assessment["id"])


def _get_insights(client, headers):
    return client.get("/api/insights/area", headers=headers)


def _insights_by_region(client, headers):
    data = _get_insights(client, headers).get_json()["data"]
    return {entry["region"]: entry for entry in data}


# ---------------------------------------------------------------------------
# 1. Per-region grouping
# ---------------------------------------------------------------------------

class TestRegionalGrouping:
    def test_no_animals_returns_empty_list(self, client):
        resp = _get_insights(client, _auth())
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_single_region_counts(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)
        _seed_assessment(app, animal_id, is_red_flag=True)
        _seed_assessment(app, animal_id)

        data = _get_insights(client, _auth()).get_json()["data"]
        assert data == [
            {"region": "Punjab", "total_assessments": 3, "flagged_cases": 1}
        ]

    def test_multiple_regions_grouped(self, app, client):
        # Punjab: two animals, three assessments, one flagged
        punjab_1 = _seed_animal(app, name="Moti", region="Punjab")
        punjab_2 = _seed_animal(app, name="Bholu", region="Punjab")
        _seed_assessment(app, punjab_1)
        _seed_assessment(app, punjab_1, is_red_flag=True)
        _seed_assessment(app, punjab_2)
        # Sindh: one animal, one assessment, not flagged
        sindh_1 = _seed_animal(app, name="Lassi", region="Sindh")
        _seed_assessment(app, sindh_1)

        by_region = _insights_by_region(client, _auth())
        assert by_region["Punjab"] == {
            "region": "Punjab", "total_assessments": 3, "flagged_cases": 1
        }
        assert by_region["Sindh"] == {
            "region": "Sindh", "total_assessments": 1, "flagged_cases": 0
        }

    def test_region_without_assessments_is_omitted(self, app, client):
        _seed_animal(app, name="Ghost", region="Balochistan")

        data = _get_insights(client, _auth()).get_json()["data"]
        assert data == []

    def test_sorted_by_total_desc_then_region_name(self, app, client):
        for region, count in (("Punjab", 2), ("Sindh", 2), ("Balochistan", 1)):
            animal_id = _seed_animal(app, name=f"A-{region}", region=region)
            for _ in range(count):
                _seed_assessment(app, animal_id)

        data = _get_insights(client, _auth()).get_json()["data"]
        assert [entry["region"] for entry in data] == [
            "Punjab", "Sindh", "Balochistan",
        ]


# ---------------------------------------------------------------------------
# 2. Flagged / urgent counting
# ---------------------------------------------------------------------------

class TestFlaggedCounting:
    def test_flagged_via_is_red_flag(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, is_red_flag=True)

        entry = _insights_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 1

    def test_flagged_via_high_urgency(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, urgency="high")

        entry = _insights_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 1

    def test_medium_urgency_is_not_flagged(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, urgency="medium")

        entry = _insights_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 0

    def test_both_conditions_counted_once(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, is_red_flag=True, urgency="high")

        entry = _insights_by_region(client, _auth())["Punjab"]
        assert entry["total_assessments"] == 1
        assert entry["flagged_cases"] == 1

    def test_mixed_flagged_and_normal(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)
        _seed_assessment(app, animal_id, urgency="high")
        _seed_assessment(app, animal_id, is_red_flag=True)
        _seed_assessment(app, animal_id)

        entry = _insights_by_region(client, _auth())["Punjab"]
        assert entry["total_assessments"] == 4
        assert entry["flagged_cases"] == 2


# ---------------------------------------------------------------------------
# 3. Animals without a region
# ---------------------------------------------------------------------------

class TestUnknownRegionBucket:
    def test_animal_without_region_buckets_as_unknown(self, app, client):
        animal_id = _seed_animal(app, region=None)
        _seed_assessment(app, animal_id, is_red_flag=True)
        _seed_assessment(app, animal_id)

        data = _get_insights(client, _auth()).get_json()["data"]
        assert data == [
            {"region": "unknown", "total_assessments": 2, "flagged_cases": 1}
        ]

    def test_known_and_unknown_regions_coexist(self, app, client):
        punjab = _seed_animal(app, name="Moti", region="Punjab")
        _seed_assessment(app, punjab)
        untracked = _seed_animal(app, name="Bholu", region=None)
        _seed_assessment(app, untracked)
        _seed_assessment(app, untracked)

        by_region = _insights_by_region(client, _auth())
        assert by_region["Punjab"]["total_assessments"] == 1
        assert by_region["unknown"]["total_assessments"] == 2


# ---------------------------------------------------------------------------
# 4. User isolation
# ---------------------------------------------------------------------------

class TestInsightIsolation:
    def test_other_users_data_excluded(self, app, client):
        # User A: one flagged assessment in Punjab
        mine = _seed_animal(app, user_id=USER_A_ID, name="Mine", region="Punjab")
        _seed_assessment(app, mine, is_red_flag=True)
        # User B: two assessments in Sindh
        theirs = _seed_animal(app, user_id=USER_B_ID, name="Theirs", region="Sindh")
        _seed_assessment(app, theirs)
        _seed_assessment(app, theirs)

        data = _get_insights(client, _auth()).get_json()["data"]
        assert data == [
            {"region": "Punjab", "total_assessments": 1, "flagged_cases": 1}
        ]

    def test_user_with_no_animals_gets_empty_list(self, app, client):
        _seed_animal(app, user_id=USER_A_ID, name="Mine", region="Punjab")
        _seed_assessment(app, _seed_animal(app, user_id=USER_A_ID, name="Second"))

        resp = _get_insights(client, _auth(USER_B_ID, USER_B_EMAIL))
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []


# ---------------------------------------------------------------------------
# 5. Auth and envelope
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_no_token(self, client):
        resp = client.get("/api/insights/area")
        assert resp.status_code == 401

    def test_garbage_token(self, client):
        resp = client.get(
            "/api/insights/area",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert resp.status_code == 401


class TestResponseEnvelope:
    def test_success_keys(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)

        body = _get_insights(client, _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "data"}
        assert body["success"] is True
        assert isinstance(body["message"], str)

    def test_entry_keys(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)

        data = _get_insights(client, _auth()).get_json()["data"]
        assert isinstance(data, list)
        assert set(data[0].keys()) == {
            "region", "total_assessments", "flagged_cases"
        }

    def test_insight_service_wiring(self, app):
        from app.services.insight_service import InsightService

        assert isinstance(app.insight_service, InsightService)

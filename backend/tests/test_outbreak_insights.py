"""
Tests for the regional outbreak insights API route
(GET /api/insights/area/outbreak).

Covers:
  1. Multi-user aggregation — data from different owners appears together
  2. Anonymization — no PII (animal names, owner IDs, assessment IDs)
  3. Per-region and per-condition grouping
  4. Flagged/urgent counting
  5. The "unknown" bucket for animals without a region
  6. Ordering, envelope shape, and auth
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
USER_A_EMAIL = "owner_a@example.com"

USER_B_ID = 2
USER_B_EMAIL = "owner_b@example.com"

USER_C_ID = 3
USER_C_EMAIL = "owner_c@example.com"


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
# Seeding helpers
# ---------------------------------------------------------------------------

def _seed_animal(app, user_id=USER_A_ID, name="Moti", region=None):
    with app.app_context():
        animal = app.animal_service.create(
            {"name": name, "animal_type": "Cow", "region": region},
            user_id=user_id,
        )
        return str(animal["id"])


def _seed_assessment(
    app,
    animal_id,
    *,
    is_red_flag=False,
    urgency="medium",
    conditions=None,
):
    if conditions is None:
        conditions = ["Sprain"]
    with app.app_context():
        assessment = app.health_assessment_repo.create({
            "animal_id": str(animal_id),
            "symptoms": "Limping on front left leg.",
            "image_ids": [],
            "status": "completed",
            "diagnosis_result": {
                "possible_conditions": conditions,
                "explanation": "Visible limp.",
                "confidence_note": "AI-assisted preliminary assessment.",
                "urgency_level": urgency,
            },
            "is_red_flag": is_red_flag,
            "red_flag_reasons": [],
        })
        return str(assessment["id"])


def _get_outbreak(client, headers):
    return client.get("/api/insights/area/outbreak", headers=headers)


def _outbreak_by_region(client, headers):
    data = _get_outbreak(client, headers).get_json()["data"]
    return {entry["region"]: entry for entry in data}


# ---------------------------------------------------------------------------
# 1. Multi-user aggregation
# ---------------------------------------------------------------------------

class TestMultiUserAggregation:
    def test_data_from_multiple_users_appears(self, app, client):
        """Assessments from different owners in the same region must
        all contribute to the aggregate count."""
        animal_a = _seed_animal(app, user_id=USER_A_ID, name="Alpha", region="Punjab")
        animal_b = _seed_animal(app, user_id=USER_B_ID, name="Beta", region="Punjab")
        animal_c = _seed_animal(app, user_id=USER_C_ID, name="Gamma", region="Punjab")

        _seed_assessment(app, animal_a)
        _seed_assessment(app, animal_b, is_red_flag=True)
        _seed_assessment(app, animal_c)

        by_region = _outbreak_by_region(client, _auth())
        assert by_region["Punjab"]["total_assessments"] == 3
        assert by_region["Punjab"]["flagged_cases"] == 1

    def test_data_from_different_regions_across_users(self, app, client):
        """Different users in different regions — each region gets its
        own aggregate regardless of who owns the animals."""
        punjab_a = _seed_animal(app, user_id=USER_A_ID, name="A1", region="Punjab")
        sindh_b = _seed_animal(app, user_id=USER_B_ID, name="B1", region="Sindh")
        _seed_assessment(app, punjab_a, is_red_flag=True)
        _seed_assessment(app, sindh_b)
        _seed_assessment(app, sindh_b, urgency="high")

        by_region = _outbreak_by_region(client, _auth(USER_C_ID, USER_C_EMAIL))
        assert by_region["Punjab"]["total_assessments"] == 1
        assert by_region["Punjab"]["flagged_cases"] == 1
        assert by_region["Sindh"]["total_assessments"] == 2
        assert by_region["Sindh"]["flagged_cases"] == 1

    def test_caller_sees_all_data_regardless_of_own_animals(self, app, client):
        """User C has no animals but still sees the full aggregate."""
        animal_a = _seed_animal(app, user_id=USER_A_ID, name="Owned", region="Punjab")
        _seed_assessment(app, animal_a, is_red_flag=True)

        resp = _get_outbreak(client, _auth(USER_C_ID, USER_C_EMAIL))
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 1
        assert data[0]["region"] == "Punjab"
        assert data[0]["total_assessments"] == 1
        assert data[0]["flagged_cases"] == 1


# ---------------------------------------------------------------------------
# 2. Anonymization — no PII
# ---------------------------------------------------------------------------

class TestAnonymization:
    def test_no_animal_names_in_response(self, app, client):
        animal_id = _seed_animal(app, name="VeryUniqueCowName", region="Punjab")
        _seed_assessment(app, animal_id)

        resp = _get_outbreak(client, _auth())
        raw = resp.data.decode("utf-8")
        assert "VeryUniqueCowName" not in raw

    def test_no_user_ids_in_response(self, app, client):
        animal_id = _seed_animal(app, user_id=USER_A_ID, region="Punjab")
        _seed_assessment(app, animal_id)

        resp = _get_outbreak(client, _auth())
        body = resp.get_json()
        raw = resp.data.decode("utf-8")
        assert str(USER_A_ID) not in raw or "user_id" not in raw
        # The response structure must never contain user_id keys
        self._assert_no_user_id_keys(body)

    def test_no_assessment_ids_in_response(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        assessment_id = _seed_assessment(app, animal_id)

        resp = _get_outbreak(client, _auth())
        raw = resp.data.decode("utf-8")
        assert f'"id": {assessment_id}' not in raw
        assert f'"assessment_id"' not in raw

    def test_no_owner_info_in_response(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)

        resp = _get_outbreak(client, _auth())
        raw = resp.data.decode("utf-8")
        for forbidden in ("owner", "email", "name", "user_id", "animal_name"):
            assert f'"{forbidden}"' not in raw

    def test_response_contains_only_aggregate_fields(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=["FMD", "BQ"])

        data = _get_outbreak(client, _auth()).get_json()["data"]
        entry = data[0]
        assert set(entry.keys()) == {
            "region", "total_assessments", "flagged_cases", "conditions"
        }
        for cond_name, cond_data in entry["conditions"].items():
            assert set(cond_data.keys()) == {"total", "flagged"}

    @staticmethod
    def _assert_no_user_id_keys(obj):
        """Recursively check that no dict in the response has a 'user_id' key."""
        if isinstance(obj, dict):
            assert "user_id" not in obj, f"Found 'user_id' key in {obj}"
            for value in obj.values():
                TestAnonymization._assert_no_user_id_keys(value)
        elif isinstance(obj, list):
            for item in obj:
                TestAnonymization._assert_no_user_id_keys(item)


# ---------------------------------------------------------------------------
# 3. Per-region and per-condition grouping
# ---------------------------------------------------------------------------

class TestRegionAndConditionGrouping:
    def test_no_animals_returns_empty_list(self, client):
        resp = _get_outbreak(client, _auth())
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_single_region_single_condition(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=["FMD"])
        _seed_assessment(app, animal_id, conditions=["FMD"], is_red_flag=True)

        by_region = _outbreak_by_region(client, _auth())
        assert by_region["Punjab"]["total_assessments"] == 2
        assert by_region["Punjab"]["flagged_cases"] == 1
        assert by_region["Punjab"]["conditions"]["FMD"] == {
            "total": 2, "flagged": 1
        }

    def test_multiple_conditions_per_assessment(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=["FMD", "BQ"])

        by_region = _outbreak_by_region(client, _auth())
        assert by_region["Punjab"]["conditions"]["FMD"]["total"] == 1
        assert by_region["Punjab"]["conditions"]["BQ"]["total"] == 1

    def test_multiple_regions_multiple_conditions(self, app, client):
        punjab = _seed_animal(app, name="A", region="Punjab")
        sindh = _seed_animal(app, name="B", region="Sindh")
        _seed_assessment(app, punjab, conditions=["FMD"], is_red_flag=True)
        _seed_assessment(app, sindh, conditions=["BQ"])

        by_region = _outbreak_by_region(client, _auth())
        assert "FMD" in by_region["Punjab"]["conditions"]
        assert "BQ" in by_region["Sindh"]["conditions"]
        assert "BQ" not in by_region["Punjab"]["conditions"]

    def test_assessment_without_conditions_skips_condition_count(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=[])

        by_region = _outbreak_by_region(client, _auth())
        assert by_region["Punjab"]["total_assessments"] == 1
        assert by_region["Punjab"]["conditions"] == {}

    def test_conditions_sorted_by_total_desc(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=["Rare"])
        _seed_assessment(app, animal_id, conditions=["Common"])
        _seed_assessment(app, animal_id, conditions=["Common"])

        by_region = _outbreak_by_region(client, _auth())
        cond_names = list(by_region["Punjab"]["conditions"].keys())
        assert cond_names == ["Common", "Rare"]


# ---------------------------------------------------------------------------
# 4. Flagged / urgent counting
# ---------------------------------------------------------------------------

class TestOutbreakFlaggedCounting:
    def test_flagged_via_is_red_flag(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, is_red_flag=True)

        entry = _outbreak_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 1

    def test_flagged_via_high_urgency(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, urgency="high")

        entry = _outbreak_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 1

    def test_medium_urgency_not_flagged(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, urgency="medium")

        entry = _outbreak_by_region(client, _auth())["Punjab"]
        assert entry["flagged_cases"] == 0

    def test_flagged_condition_breakdown(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id, conditions=["FMD"], is_red_flag=True)
        _seed_assessment(app, animal_id, conditions=["FMD"])
        _seed_assessment(app, animal_id, conditions=["BQ"], urgency="high")

        conds = _outbreak_by_region(client, _auth())["Punjab"]["conditions"]
        assert conds["FMD"] == {"total": 2, "flagged": 1}
        assert conds["BQ"] == {"total": 1, "flagged": 1}


# ---------------------------------------------------------------------------
# 5. Unknown region bucket
# ---------------------------------------------------------------------------

class TestOutbreakUnknownRegion:
    def test_animal_without_region_buckets_as_unknown(self, app, client):
        animal_id = _seed_animal(app, region=None)
        _seed_assessment(app, animal_id, is_red_flag=True)

        data = _get_outbreak(client, _auth()).get_json()["data"]
        assert len(data) == 1
        assert data[0]["region"] == "unknown"
        assert data[0]["flagged_cases"] == 1

    def test_known_and_unknown_regions_coexist(self, app, client):
        punjab = _seed_animal(app, name="A", region="Punjab")
        unknown = _seed_animal(app, name="B", region=None)
        _seed_assessment(app, punjab)
        _seed_assessment(app, unknown)

        by_region = _outbreak_by_region(client, _auth())
        assert "Punjab" in by_region
        assert "unknown" in by_region


# ---------------------------------------------------------------------------
# 6. Ordering and envelope
# ---------------------------------------------------------------------------

class TestOutbreakOrdering:
    def test_sorted_by_total_desc_then_region_name(self, app, client):
        for region, count in (("Punjab", 3), ("Sindh", 3), ("Balochistan", 1)):
            animal_id = _seed_animal(app, name=f"A-{region}", region=region)
            for _ in range(count):
                _seed_assessment(app, animal_id)

        data = _get_outbreak(client, _auth()).get_json()["data"]
        assert [e["region"] for e in data] == [
            "Punjab", "Sindh", "Balochistan",
        ]


class TestOutbreakAuth:
    def test_no_token(self, client):
        resp = client.get("/api/insights/area/outbreak")
        assert resp.status_code == 401

    def test_garbage_token(self, client):
        resp = client.get(
            "/api/insights/area/outbreak",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        assert resp.status_code == 401

    def test_empty_bearer(self, client):
        resp = client.get(
            "/api/insights/area/outbreak",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401


class TestOutbreakEnvelope:
    def test_success_keys(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)

        body = _get_outbreak(client, _auth()).get_json()
        assert set(body.keys()) == {"success", "message", "data"}
        assert body["success"] is True
        assert isinstance(body["message"], str)

    def test_entry_keys(self, app, client):
        animal_id = _seed_animal(app, region="Punjab")
        _seed_assessment(app, animal_id)

        data = _get_outbreak(client, _auth()).get_json()["data"]
        assert isinstance(data, list)
        assert set(data[0].keys()) == {
            "region", "total_assessments", "flagged_cases", "conditions"
        }

    def test_existing_area_endpoint_unchanged(self, app, client):
        """The original /insights/area must still be user-scoped."""
        mine = _seed_animal(app, user_id=USER_A_ID, region="Punjab")
        theirs = _seed_animal(app, user_id=USER_B_ID, region="Punjab")
        _seed_assessment(app, mine)
        _seed_assessment(app, theirs)
        _seed_assessment(app, theirs)

        # User-scoped endpoint
        scoped = client.get("/api/insights/area", headers=_auth()).get_json()["data"]
        assert scoped[0]["total_assessments"] == 1

        # Cross-user endpoint
        outbreak = _get_outbreak(client, _auth()).get_json()["data"]
        assert outbreak[0]["total_assessments"] == 3

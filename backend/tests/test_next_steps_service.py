"""
Tests for the safe_next_steps guidance attached to health assessments.

Covers:
  1. Unit tests for build_safe_next_steps — tier selection (emergency /
     medium / low), bilingual parallel lists, copy safety, safe defaults
  2. Endpoint tests — POST /api/animals/<id>/assessments always attaches
     guidance to diagnosis_result:
       - on the AI-fallback path (stub provider, status "failed")
       - escalated to the emergency tier for red-flag symptoms
       - merged into a completed (non-fallback) AI result
       - persisted and returned by GET /api/assessments/<id>
"""

import io
from datetime import datetime, timedelta, timezone

import cv2
import jwt
import numpy as np
import pytest
from app import create_app
from app.config import TestingConfig
from app.services.health_assessment_service import HealthAssessmentService
from app.services.next_steps_service import build_safe_next_steps

# ---------------------------------------------------------------------------
# Shared constants — first step of each tier, used as tier fingerprints
# ---------------------------------------------------------------------------

EMERGENCY_FIRST_STEP = (
    "Contact a veterinarian immediately — the reported signs may indicate an emergency."
)
MEDIUM_FIRST_STEP = "Arrange a veterinary check-up within the next day or two."
LOW_FIRST_STEP = "Keep monitoring the animal over the next few days."


# ---------------------------------------------------------------------------
# 1. Unit tests — build_safe_next_steps
# ---------------------------------------------------------------------------

class TestTierSelection:
    """Red-flag / urgency inputs must select the correct guidance tier."""

    def test_red_flag_escalates_to_emergency(self):
        result = build_safe_next_steps(urgency_level="medium", is_red_flag=True)
        assert result["safe_next_steps"][0] == EMERGENCY_FIRST_STEP

    def test_red_flag_escalates_even_without_urgency(self):
        result = build_safe_next_steps(urgency_level=None, is_red_flag=True)
        assert result["safe_next_steps"][0] == EMERGENCY_FIRST_STEP

    def test_high_urgency_escalates_to_emergency(self):
        result = build_safe_next_steps(urgency_level="high", is_red_flag=False)
        assert result["safe_next_steps"][0] == EMERGENCY_FIRST_STEP

    def test_medium_urgency_selects_medium_tier(self):
        result = build_safe_next_steps(urgency_level="medium", is_red_flag=False)
        assert result["safe_next_steps"][0] == MEDIUM_FIRST_STEP

    def test_low_urgency_selects_low_tier(self):
        result = build_safe_next_steps(urgency_level="low", is_red_flag=False)
        assert result["safe_next_steps"][0] == LOW_FIRST_STEP

    @pytest.mark.parametrize("urgency", [None, "", "unknown", "URGENT", 5])
    def test_unrecognized_urgency_defaults_to_medium(self, urgency):
        result = build_safe_next_steps(urgency_level=urgency, is_red_flag=False)
        assert result["safe_next_steps"][0] == MEDIUM_FIRST_STEP


class TestBilingualShape:
    """The returned dict must be well-formed and parallel in both languages."""

    @pytest.mark.parametrize("urgency,is_red_flag", [
        ("high", False),
        ("medium", True),
        ("medium", False),
        ("low", False),
        (None, False),
    ])
    def test_keys_and_parallel_lists(self, urgency, is_red_flag):
        result = build_safe_next_steps(urgency_level=urgency, is_red_flag=is_red_flag)
        assert set(result.keys()) == {"safe_next_steps", "safe_next_steps_urdu"}

        english, urdu = result["safe_next_steps"], result["safe_next_steps_urdu"]
        assert isinstance(english, list) and len(english) > 0
        assert isinstance(urdu, list) and len(urdu) == len(english)
        for step in english + urdu:
            assert isinstance(step, str) and step.strip()

    def test_every_tier_tells_farmer_to_seek_professional_help(self):
        """All tiers must point the farmer toward a veterinarian."""
        for urgency, is_red_flag in (
            ("high", False), ("medium", False), ("low", False),
        ):
            english = build_safe_next_steps(urgency, is_red_flag)["safe_next_steps"]
            joined = " ".join(english).lower()
            assert "veterinar" in joined, (
                f"Tier for urgency={urgency!r} lacks professional-help guidance"
            )


class TestCopySafety:
    """Mutating a returned list must not corrupt guidance for later calls."""

    def test_returned_lists_are_copies(self):
        first = build_safe_next_steps(urgency_level="low", is_red_flag=False)
        first["safe_next_steps"].clear()
        first["safe_next_steps_urdu"].append("tampered")

        second = build_safe_next_steps(urgency_level="low", is_red_flag=False)
        assert second["safe_next_steps"][0] == LOW_FIRST_STEP
        assert len(second["safe_next_steps_urdu"]) == len(second["safe_next_steps"])
        assert "tampered" not in second["safe_next_steps_urdu"]


# ---------------------------------------------------------------------------
# 2. Endpoint tests — guidance is attached to diagnosis_result
# ---------------------------------------------------------------------------

def _token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, TestingConfig.SECRET_KEY, algorithm="HS256")


def _auth(user_id=1, email="owner@example.com"):
    return {"Authorization": f"Bearer {_token(user_id, email)}"}


@pytest.fixture
def app():
    """Fresh app per test, with a working stub image-storage service."""
    application = create_app("testing")

    class _StubStorage:
        def save_image(self, file_stream, filename, content_type):
            return "img_stub_001"

    application.image_storage_service = _StubStorage()
    return application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


def _seed_animal(app, user_id=1):
    with app.app_context():
        animal = app.animal_service.create(
            {"name": "Moti", "animal_type": "Cow"}, user_id=user_id
        )
        return str(animal["id"])


def _make_jpeg() -> bytes:
    """Bright noisy 400x400 JPEG that passes the image quality gate."""
    rng = np.random.default_rng(42)
    image = rng.integers(120, 220, (400, 400, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", image)
    assert ok
    return buf.tobytes()


def _post_assessment(client, animal_id, symptoms):
    return client.post(
        f"/api/animals/{animal_id}/assessments",
        headers=_auth(),
        data={
            "symptoms": symptoms,
            "image": (io.BytesIO(_make_jpeg()), "photo.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
    )


class TestFallbackPathIncludesGuidance:
    """Testing stub provider returns the AI fallback — guidance must still appear."""

    def test_fallback_assessment_has_safe_next_steps(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_assessment(client, animal_id, "Limping slightly on the front left leg.")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["data"]["status"] == "failed"  # stub provider → AI fallback

        diagnosis = body["data"]["diagnosis_result"]
        assert diagnosis["safe_next_steps"][0] == MEDIUM_FIRST_STEP
        assert len(diagnosis["safe_next_steps_urdu"]) == len(diagnosis["safe_next_steps"])

    def test_red_flag_symptoms_escalate_to_emergency_tier(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_assessment(client, animal_id, "The goat is gasping and can't stand up.")

        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["is_red_flag"] is True

        diagnosis = data["diagnosis_result"]
        assert diagnosis["safe_next_steps"][0] == EMERGENCY_FIRST_STEP
        assert diagnosis["safe_next_steps_urdu"][0].startswith("فوراً")


class TestCompletedPathIncludesGuidance:
    """A non-fallback AI result must get the guidance merged in."""

    def test_completed_assessment_has_safe_next_steps(self, app, client):
        class _CompletedProvider:
            def assess(self, image_bytes, image_content_type, symptoms):
                return {
                    "possible_conditions": ["Minor sprain"],
                    "explanation": "Mild limp consistent with a minor sprain.",
                    "confidence_note": "AI-assisted preliminary assessment.",
                    "urgency_level": "low",
                }

        app.health_assessment_service = HealthAssessmentService(_CompletedProvider())
        animal_id = _seed_animal(app)
        resp = _post_assessment(client, animal_id, "Slight limp, still eating well.")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["data"]["status"] == "completed"

        diagnosis = body["data"]["diagnosis_result"]
        assert diagnosis["possible_conditions"] == ["Minor sprain"]  # AI result intact
        assert diagnosis["safe_next_steps"][0] == LOW_FIRST_STEP
        assert len(diagnosis["safe_next_steps_urdu"]) == len(diagnosis["safe_next_steps"])

    def test_completed_high_urgency_gets_emergency_guidance(self, app, client):
        class _HighUrgencyProvider:
            def assess(self, image_bytes, image_content_type, symptoms):
                return {
                    "possible_conditions": ["Acute infection"],
                    "explanation": "Rapid deterioration visible in the image.",
                    "confidence_note": "AI-assisted preliminary assessment.",
                    "urgency_level": "high",
                }

        app.health_assessment_service = HealthAssessmentService(_HighUrgencyProvider())
        animal_id = _seed_animal(app)
        resp = _post_assessment(client, animal_id, "Swollen jaw, not eating at all.")

        data = resp.get_json()["data"]
        assert data["is_red_flag"] is True
        assert data["diagnosis_result"]["safe_next_steps"][0] == EMERGENCY_FIRST_STEP


class TestGuidancePersists:
    """Guidance must be persisted with the record, not just merged into the response."""

    def test_get_assessment_returns_safe_next_steps(self, app, client):
        animal_id = _seed_animal(app)
        created = _post_assessment(client, animal_id, "Limping slightly.")
        assessment_id = created.get_json()["data"]["id"]

        resp = client.get(f"/api/assessments/{assessment_id}", headers=_auth())

        assert resp.status_code == 200
        diagnosis = resp.get_json()["data"]["diagnosis_result"]
        assert diagnosis["safe_next_steps"][0] == MEDIUM_FIRST_STEP
        assert len(diagnosis["safe_next_steps_urdu"]) == len(diagnosis["safe_next_steps"])

    def test_list_assessments_include_safe_next_steps(self, app, client):
        animal_id = _seed_animal(app)
        _post_assessment(client, animal_id, "Limping slightly.")

        resp = client.get(f"/api/animals/{animal_id}/assessments", headers=_auth())

        assert resp.status_code == 200
        records = resp.get_json()["data"]
        assert len(records) == 1
        assert records[0]["diagnosis_result"]["safe_next_steps"][0] == MEDIUM_FIRST_STEP

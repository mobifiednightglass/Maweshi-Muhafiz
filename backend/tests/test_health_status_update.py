"""
Tests for animal health_status auto-update after health assessments.

health_status always reflects the most recent successfully completed
assessment result:
  - high/medium urgency OR is_red_flag=True  →  "Needs Attention"
  - low urgency + no red flag                →  "Healthy"
  - failed assessments never change the existing status

Covers:
  1. High urgency → "Needs Attention"
  2. Medium urgency → "Needs Attention"
  3. Red-flag keywords → "Needs Attention"
  4. Low urgency + no red flag → "Healthy"
  5. Needs Attention + low urgency → "Healthy"
  6. Needs Attention + medium urgency → remains "Needs Attention"
  7. Failed assessment → status unchanged (both directions)
  8. Ownership isolation
  9. Voice endpoint shares the same pipeline logic
"""

import io
from datetime import datetime, timedelta, timezone

import cv2
import jwt
import numpy as np
import pytest
from app import create_app
from app.config import TestingConfig

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

USER_A_ID = 1
USER_A_EMAIL = "owner@example.com"


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
# Fake providers
# ---------------------------------------------------------------------------

class _StubStorage:
    """Replaces ImageStorageService in tests — returns a canned file id."""

    def save_image(self, file_stream, filename, content_type):
        return "img_stub_001"

    def delete_image(self, file_id):
        pass


class _FakeHealthAssessmentService:
    """Returns a canned diagnosis_result so tests control urgency_level."""

    def __init__(self, diagnosis_result):
        self._result = diagnosis_result

    def run_assessment(self, image_bytes, image_content_type, symptoms):
        return self._result


def _diagnosis(urgency_level="low"):
    """Build a minimal valid diagnosis_result dict."""
    return {
        "possible_conditions": ["Test condition"],
        "explanation": "Test explanation.",
        "confidence_note": "AI-assisted preliminary assessment.",
        "urgency_level": urgency_level,
        "image_too_blurry": False,
        "contains_animal": True,
        "possible_conditions_urdu": ["ٹیسٹ حالت"],
        "explanation_urdu": "ٹیسٹ وضاحت۔",
        "confidence_note_urdu": "ٹیسٹ اعتماد نوٹ۔",
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Fresh app per test with stub image storage."""
    application = create_app("testing")
    application.image_storage_service = _StubStorage()
    return application


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_animal(app, user_id=USER_A_ID, health_status="Healthy"):
    with app.app_context():
        animal = app.animal_service.create(
            {"name": "Moti", "animal_type": "Cow", "health_status": health_status},
            user_id=user_id,
        )
        return str(animal["id"])


def _make_jpeg() -> bytes:
    """Bright noisy 400×400 JPEG that passes the image quality gate."""
    rng = np.random.default_rng(42)
    image = rng.integers(120, 220, (400, 400, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", image)
    assert ok
    return buf.tobytes()


def _post_assessment(client, animal_id, symptoms="Limping.", auth=None):
    """POST a text+image assessment to the standard endpoint."""
    return client.post(
        f"/api/animals/{animal_id}/assessments",
        headers=auth if auth is not None else _auth(),
        data={
            "symptoms": symptoms,
            "image": (io.BytesIO(_make_jpeg()), "photo.jpg", "image/jpeg"),
        },
        content_type="multipart/form-data",
    )


def _get_animal_status(client, animal_id, auth=None):
    """GET the animal and return its current health_status."""
    resp = client.get(
        f"/api/animals/{animal_id}",
        headers=auth if auth is not None else _auth(),
    )
    return resp.get_json()["data"]["health_status"]


# ---------------------------------------------------------------------------
# 1. High urgency → "Needs Attention"
# ---------------------------------------------------------------------------

class TestHighUrgencyUpdatesStatus:
    def test_high_urgency_sets_needs_attention(self, app, client):
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="high"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        resp = _post_assessment(client, animal_id)
        assert resp.status_code == 200

        assert _get_animal_status(client, animal_id) == "Needs Attention"

    def test_high_urgency_overrides_sick_status(self, app, client):
        """Even if the animal was 'Sick', a high-urgency result escalates."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="high"),
        )
        animal_id = _seed_animal(app, health_status="Sick")

        _post_assessment(client, animal_id)

        assert _get_animal_status(client, animal_id) == "Needs Attention"


# ---------------------------------------------------------------------------
# 2. Red-flag keywords + low AI urgency → "Needs Attention"
# ---------------------------------------------------------------------------

class TestRedFlagKeywordsUpdateStatus:
    def test_red_flag_keywords_set_needs_attention(self, app, client):
        """Symptoms contain a red-flag keyword; AI urgency is low."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="low"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        # "gasping" is a red-flag keyword
        resp = _post_assessment(client, animal_id, symptoms="The animal is gasping")
        assert resp.status_code == 200

        assert _get_animal_status(client, animal_id) == "Needs Attention"

    def test_urdu_red_flag_keyword_sets_needs_attention(self, app, client):
        """Urdu red-flag keyword also triggers the update."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="low"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        # Urdu keyword for "difficulty breathing"
        resp = _post_assessment(
            client, animal_id,
            symptoms="جانور کو سانس لینے میں دشواری ہے",
        )
        assert resp.status_code == 200

        assert _get_animal_status(client, animal_id) == "Needs Attention"


# ---------------------------------------------------------------------------
# 3. Low urgency + no red flag → no change
# ---------------------------------------------------------------------------

class TestLowUrgencyNoChange:
    def test_low_urgency_preserves_healthy(self, app, client):
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="low"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        _post_assessment(client, animal_id, symptoms="Mild cough.")

        assert _get_animal_status(client, animal_id) == "Healthy"


class TestLowUrgencyDowngrade:
    def test_low_urgency_resets_needs_attention_to_healthy(self, app, client):
        """Latest completed low-urgency assessment clears 'Needs Attention'."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="low"),
        )
        animal_id = _seed_animal(app, health_status="Needs Attention")

        _post_assessment(client, animal_id, symptoms="Mild cough.")

        assert _get_animal_status(client, animal_id) == "Healthy"


# ---------------------------------------------------------------------------
# 4. Medium urgency → "Needs Attention"
# ---------------------------------------------------------------------------

class TestMediumUrgencyUpdatesStatus:
    def test_healthy_plus_medium_urgency_sets_needs_attention(self, app, client):
        """Medium urgency without red flag still escalates to 'Needs Attention'."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="medium"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        _post_assessment(client, animal_id, symptoms="Slight limp.")

        assert _get_animal_status(client, animal_id) == "Needs Attention"

    def test_needs_attention_plus_medium_urgency_remains(self, app, client):
        """Medium urgency preserves existing 'Needs Attention'."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="medium"),
        )
        animal_id = _seed_animal(app, health_status="Needs Attention")

        _post_assessment(client, animal_id, symptoms="Slight limp.")

        assert _get_animal_status(client, animal_id) == "Needs Attention"


# ---------------------------------------------------------------------------
# 5. Failed assessment → no change
# ---------------------------------------------------------------------------

class TestFailedAssessmentNoChange:
    def test_failed_assessment_preserves_status(self, app, client):
        """Stub provider returns safe_fallback → status='failed' → no update."""
        # The default _StubVisionProvider in testing mode returns safe_fallback,
        # which the pipeline marks as status="failed".  We let it through
        # without overriding health_assessment_service.
        animal_id = _seed_animal(app, health_status="Healthy")

        resp = _post_assessment(client, animal_id)
        assert resp.status_code == 200

        assessment = resp.get_json()["data"]
        assert assessment["status"] == "failed"

        # Status must remain unchanged
        assert _get_animal_status(client, animal_id) == "Healthy"

    def test_failed_with_red_flag_keywords_still_no_change(self, app, client):
        """Even with red-flag keywords, a failed AI assessment must not update."""
        # Use stub provider (returns fallback → failed).  Symptoms contain
        # a red-flag keyword, so final_is_red_flag=True, but status_value
        # is "failed" — the guard must prevent the update.
        animal_id = _seed_animal(app, health_status="Healthy")

        resp = _post_assessment(
            client, animal_id, symptoms="The animal is gasping",
        )
        assert resp.status_code == 200

        assessment = resp.get_json()["data"]
        assert assessment["status"] == "failed"

        # The red-flag keyword is captured on the assessment record...
        assert assessment["is_red_flag"] is True
        # ...but the animal's health_status is NOT changed because the
        # assessment itself failed.
        assert _get_animal_status(client, animal_id) == "Healthy"

    def test_failed_after_needs_attention_preserves_status(self, app, client):
        """A failed assessment must not clear an existing 'Needs Attention'."""
        animal_id = _seed_animal(app, health_status="Needs Attention")

        resp = _post_assessment(client, animal_id)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["status"] == "failed"

        assert _get_animal_status(client, animal_id) == "Needs Attention"


# ---------------------------------------------------------------------------
# 6. Ownership isolation
# ---------------------------------------------------------------------------

class TestOwnershipIsolation:
    def test_other_users_animal_not_affected(self, app, client):
        """Assessment on user A's animal must not touch user B's animal."""
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="high"),
        )
        animal_a = _seed_animal(app, user_id=1, health_status="Healthy")
        animal_b = _seed_animal(app, user_id=2, health_status="Healthy")

        # User 1 submits a high-urgency assessment on their own animal
        _post_assessment(client, animal_a, auth=_auth(user_id=1))

        # User 1's animal should be updated
        assert _get_animal_status(client, animal_a, auth=_auth(user_id=1)) == "Needs Attention"

        # User 2's animal must remain unchanged
        assert _get_animal_status(
            client, animal_b,
            auth=_auth(user_id=2, email="other@example.com"),
        ) == "Healthy"


# ---------------------------------------------------------------------------
# 7. Voice endpoint shares the same pipeline
# ---------------------------------------------------------------------------

class TestVoiceEndpointSharesPipeline:
    def test_voice_assessment_high_urgency_updates_status(self, app, client):
        """The voice endpoint goes through _run_assessment_pipeline too."""
        from app.services.voice_service import TESTING_TRANSCRIPTION, VoiceService

        class _FakeSTT:
            def transcribe(self, audio_bytes, mime_type):
                return TESTING_TRANSCRIPTION

        class _FakeTTS:
            def synthesize_speech(self, text):
                return b"\x00\x00" * 2400

        app.voice_service = VoiceService(_FakeSTT(), _FakeTTS())
        app.health_assessment_service = _FakeHealthAssessmentService(
            _diagnosis(urgency_level="high"),
        )
        animal_id = _seed_animal(app, health_status="Healthy")

        resp = client.post(
            f"/api/animals/{animal_id}/symptoms/voice",
            headers=_auth(),
            data={
                "audio": (io.BytesIO(b"fake-audio"), "note.mp4", "audio/mp4"),
                "image": (io.BytesIO(_make_jpeg()), "photo.jpg", "image/jpeg"),
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200

        assert _get_animal_status(client, animal_id) == "Needs Attention"

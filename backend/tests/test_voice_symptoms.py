"""
Tests for the voice-symptoms flow.

Covers:
  1. Unit tests for the voice service — MIME resolution, PCM→WAV wrapping,
     VoiceService error taxonomy (no Gemini calls; fake providers only)
  2. Endpoint tests — POST /api/animals/<id>/symptoms/voice:
       - happy path returns transcribed text + assessment with guidance
       - WhatsApp voice notes (.mp4 with non-audio content type) are accepted
       - the transcript is persisted as the record's symptoms
       - Urdu red-flag transcripts escalate to the emergency tier
       - no-speech / empty / bad-format audio → 400
       - provider failure → 502
       - missing fields / missing auth / wrong owner → 400 / 401 / 404
  3. Endpoint tests — GET /api/animals/<id>/assessments/<id>/speech:
       - returns the Urdu guidance spoken as a WAV (mocked TTS)
       - 401 / 404 ownership and not-found paths
       - legacy assessments without Urdu guidance → 404
       - TTS provider failure → 502
"""

import io
import wave
from datetime import datetime, timedelta, timezone

import cv2
import jwt
import numpy as np
import pytest
from app import create_app
from app.config import TestingConfig
from app.services.voice_service import (
    TESTING_TRANSCRIPTION,
    TTS_SAMPLE_RATE,
    AudioFormatError,
    NoSpeechDetectedError,
    SpeechSynthesisError,
    TranscriptionError,
    VoiceService,
    resolve_audio_mime_type,
    wrap_pcm_as_wav,
)

EMERGENCY_FIRST_STEP = (
    "Contact a veterinarian immediately — the reported signs may indicate an emergency."
)
MEDIUM_FIRST_STEP = "Arrange a veterinary check-up within the next day or two."

# An Urdu red-flag phrase present in RED_FLAG_KEYWORDS ("difficulty breathing").
URDU_RED_FLAG_KEYWORD = "سانس لینے میں دشواری"
URDU_RED_FLAG_SYMPTOMS = f"جانور کو {URDU_RED_FLAG_KEYWORD} ہے"


# ---------------------------------------------------------------------------
# Fake providers — no real Gemini calls anywhere in this file
# ---------------------------------------------------------------------------

class _FakeSTTProvider:
    """Returns a canned transcript and records how it was called."""

    def __init__(self, transcript=TESTING_TRANSCRIPTION):
        self.transcript = transcript
        self.calls = []

    def transcribe(self, audio_bytes, mime_type):
        self.calls.append({"audio_bytes": audio_bytes, "mime_type": mime_type})
        return self.transcript


class _RaisingSTTProvider:
    def __init__(self, exc):
        self.exc = exc

    def transcribe(self, audio_bytes, mime_type):
        raise self.exc


class _RecordingTTSProvider:
    """Returns canned PCM and records the text it was asked to speak."""

    def __init__(self, pcm=b"\x00\x01" * 100):
        self.pcm = pcm
        self.spoken_texts = []

    def synthesize_speech(self, text):
        self.spoken_texts.append(text)
        return self.pcm


class _RaisingTTSProvider:
    def __init__(self, exc):
        self.exc = exc

    def synthesize_speech(self, text):
        raise self.exc


class _FakeTTSProvider:
    def __init__(self, pcm=b"\x01\x02\x03\x04"):
        self.pcm = pcm

    def synthesize_speech(self, text):
        return self.pcm


def _voice_service(stt, tts=None):
    return VoiceService(stt, tts or _FakeTTSProvider())


# ---------------------------------------------------------------------------
# 1. Unit tests — MIME resolution and WAV wrapping
# ---------------------------------------------------------------------------

class TestResolveAudioMimeType:
    @pytest.mark.parametrize("filename,content_type,expected", [
        ("note.wav", "audio/wav", "audio/wav"),
        ("anything", "audio/mpeg", "audio/mpeg"),
        ("note.wav", "audio/wav; charset=binary", "audio/wav"),  # params stripped
        ("note.mp4", None, "audio/mp4"),          # WhatsApp voice note
        ("note.mp4", "video/mp4", "audio/mp4"),   # ... even if it looks like video
        ("note.m4a", "application/octet-stream", "audio/mp4"),
        ("note.ogg", None, "audio/ogg"),
        ("note.webm", None, "audio/webm"),
    ])
    def test_resolves_expected_mime(self, filename, content_type, expected):
        assert resolve_audio_mime_type(filename, content_type) == expected

    @pytest.mark.parametrize("filename,content_type", [
        ("notes.txt", "text/plain"),
        ("photo.jpg", "image/jpeg"),
        ("document.pdf", None),
        (None, None),
        ("", "application/octet-stream"),
    ])
    def test_unrecognisable_formats_raise(self, filename, content_type):
        with pytest.raises(AudioFormatError):
            resolve_audio_mime_type(filename, content_type)


class TestWrapPcmAsWav:
    def test_wrapped_wav_has_gemini_tts_parameters(self):
        pcm = b"\x00\x01" * 1000
        wav_bytes = wrap_pcm_as_wav(pcm)

        assert wav_bytes[:4] == b"RIFF"  # recognizable WAV container
        with wave.open(io.BytesIO(wav_bytes)) as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == TTS_SAMPLE_RATE
            assert wav_file.readframes(wav_file.getnframes()) == pcm


# ---------------------------------------------------------------------------
# 2. Unit tests — VoiceService error taxonomy
# ---------------------------------------------------------------------------

class TestTranscribeUrduAudio:
    def test_returns_stripped_transcript(self):
        service = _voice_service(_FakeSTTProvider("  کچھ متن  "))
        assert service.transcribe_urdu_audio(b"abc", "note.mp4", "audio/mp4") == "کچھ متن"

    def test_passes_resolved_mime_to_provider(self):
        provider = _FakeSTTProvider()
        _voice_service(provider).transcribe_urdu_audio(b"abc", "note.mp4", "video/mp4")
        assert provider.calls[0]["mime_type"] == "audio/mp4"
        assert provider.calls[0]["audio_bytes"] == b"abc"

    def test_empty_audio_bytes_raise(self):
        with pytest.raises(AudioFormatError):
            _voice_service(_FakeSTTProvider()).transcribe_urdu_audio(b"", "note.mp4")

    @pytest.mark.parametrize("provider_answer", ["", "   ", "NO_SPEECH_DETECTED"])
    def test_no_speech_variants_raise(self, provider_answer):
        service = _voice_service(_FakeSTTProvider(provider_answer))
        with pytest.raises(NoSpeechDetectedError):
            service.transcribe_urdu_audio(b"abc", "note.mp4", "audio/mp4")

    def test_bad_format_raises_before_provider_is_called(self):
        provider = _FakeSTTProvider()
        service = _voice_service(provider)
        with pytest.raises(AudioFormatError):
            service.transcribe_urdu_audio(b"abc", "note.txt", "text/plain")
        assert provider.calls == []  # no wasted AI call

    def test_provider_failure_raises_transcription_error(self):
        service = _voice_service(_RaisingSTTProvider(TranscriptionError("boom")))
        with pytest.raises(TranscriptionError):
            service.transcribe_urdu_audio(b"abc", "note.mp4", "audio/mp4")

    def test_unexpected_provider_error_is_wrapped(self):
        service = _voice_service(_RaisingSTTProvider(RuntimeError("network down")))
        with pytest.raises(TranscriptionError):
            service.transcribe_urdu_audio(b"abc", "note.mp4", "audio/mp4")


class TestUrduTextToSpeech:
    def test_returns_wav_wrapping_provider_pcm(self):
        pcm = b"\x00\x01" * 500
        wav_bytes = _voice_service(_FakeSTTProvider(), _FakeTTSProvider(pcm)) \
            .urdu_text_to_speech("سلام")

        with wave.open(io.BytesIO(wav_bytes)) as wav_file:
            assert wav_file.readframes(wav_file.getnframes()) == pcm

    @pytest.mark.parametrize("text", ["", "   ", None])
    def test_empty_text_raises(self, text):
        with pytest.raises(SpeechSynthesisError):
            _voice_service(_FakeSTTProvider()).urdu_text_to_speech(text)

    def test_provider_returning_no_audio_raises(self):
        with pytest.raises(SpeechSynthesisError):
            _voice_service(_FakeSTTProvider(), _FakeTTSProvider(b"")) \
                .urdu_text_to_speech("سلام")

    def test_unexpected_provider_error_is_wrapped(self):
        class _ExplodingTTS:
            def synthesize_speech(self, text):
                raise RuntimeError("quota exhausted")

        with pytest.raises(SpeechSynthesisError):
            _voice_service(_FakeSTTProvider(), _ExplodingTTS()).urdu_text_to_speech("سلام")


# ---------------------------------------------------------------------------
# 3. Endpoint tests — POST /api/animals/<animal_id>/symptoms/voice
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


def _post_voice(
    client,
    animal_id,
    audio=b"fake-audio-bytes",
    audio_filename="note.mp4",
    audio_content_type="audio/mp4",
    auth=None,
    include_audio=True,
    include_image=True,
):
    data = {}
    if include_audio:
        data["audio"] = (io.BytesIO(audio), audio_filename, audio_content_type)
    if include_image:
        data["image"] = (io.BytesIO(_make_jpeg()), "photo.jpg", "image/jpeg")
    return client.post(
        f"/api/animals/{animal_id}/symptoms/voice",
        headers=auth if auth is not None else _auth(),
        data=data,
        content_type="multipart/form-data",
    )


class TestVoiceAssessmentHappyPath:
    def test_returns_transcript_and_assessment_with_guidance(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id)

        assert resp.status_code == 200
        body = resp.get_json()
        data = body["data"]
        assert data["transcribed_symptoms"] == TESTING_TRANSCRIPTION

        assessment = data["assessment"]
        assert assessment["symptoms"] == TESTING_TRANSCRIPTION
        assert assessment["status"] == "failed"  # stub vision provider → fallback
        assert assessment["is_red_flag"] is False
        assert assessment["diagnosis_result"]["safe_next_steps"][0] == MEDIUM_FIRST_STEP
        assert len(assessment["diagnosis_result"]["safe_next_steps_urdu"]) == \
            len(assessment["diagnosis_result"]["safe_next_steps"])

    def test_whatsapp_voice_note_mp4_with_video_content_type(self, app, client):
        """Real WhatsApp uploads often arrive as video/mp4 — must still work."""
        animal_id = _seed_animal(app)
        resp = _post_voice(
            client, animal_id,
            audio_filename="msg0001.mp4",
            audio_content_type="video/mp4",
        )

        assert resp.status_code == 200
        assert resp.get_json()["data"]["transcribed_symptoms"] == TESTING_TRANSCRIPTION

    def test_transcript_persisted_and_readable_via_get(self, app, client):
        animal_id = _seed_animal(app)
        created = _post_voice(client, animal_id)
        assessment_id = created.get_json()["data"]["assessment"]["id"]

        resp = client.get(f"/api/assessments/{assessment_id}", headers=_auth())

        assert resp.status_code == 200
        record = resp.get_json()["data"]
        assert record["symptoms"] == TESTING_TRANSCRIPTION
        assert record["diagnosis_result"]["safe_next_steps"][0] == MEDIUM_FIRST_STEP

    def test_urdu_red_flag_transcript_escalates_to_emergency(self, app, client):
        app.voice_service = _voice_service(_FakeSTTProvider(URDU_RED_FLAG_SYMPTOMS))
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id)

        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["transcribed_symptoms"] == URDU_RED_FLAG_SYMPTOMS

        assessment = data["assessment"]
        assert assessment["is_red_flag"] is True
        assert URDU_RED_FLAG_KEYWORD in assessment["red_flag_reasons"]
        assert assessment["diagnosis_result"]["safe_next_steps"][0] == EMERGENCY_FIRST_STEP
        assert assessment["diagnosis_result"]["safe_next_steps_urdu"][0].startswith("فوراً")


class TestVoiceAssessmentClientErrors:
    @pytest.mark.parametrize("provider_answer", ["", "NO_SPEECH_DETECTED"])
    def test_no_speech_detected_returns_400(self, app, client, provider_answer):
        app.voice_service = _voice_service(_FakeSTTProvider(provider_answer))
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id)

        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False
        assert "No understandable speech" in body["message"]

    def test_unsupported_audio_format_returns_400(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(
            client, animal_id,
            audio_filename="note.txt",
            audio_content_type="text/plain",
        )

        assert resp.status_code == 400
        assert "Unsupported audio format" in resp.get_json()["message"]

    def test_empty_audio_file_returns_400(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id, audio=b"")

        assert resp.status_code == 400

    def test_missing_audio_field_returns_400(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id, include_audio=False)

        assert resp.status_code == 400
        assert "'audio' file field is required" in resp.get_json()["message"]

    def test_missing_image_field_returns_400(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id, include_image=False)

        assert resp.status_code == 400
        assert "'image' file field is required" in resp.get_json()["message"]

    def test_no_auth_returns_401(self, app, client):
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id, auth={})

        assert resp.status_code == 401


class TestVoiceAssessmentAnimalOwnership:
    def test_unknown_animal_returns_404(self, app, client):
        resp = _post_voice(client, "no-such-animal")
        assert resp.status_code == 404

    def test_other_users_animal_returns_404(self, app, client):
        animal_id = _seed_animal(app, user_id=1)
        resp = _post_voice(client, animal_id, auth=_auth(user_id=2, email="other@example.com"))

        assert resp.status_code == 404

    def test_no_assessment_created_when_transcription_fails(self, app, client):
        """A failed transcription must not leave a stray record behind."""
        app.voice_service = _voice_service(_RaisingSTTProvider(TranscriptionError("boom")))
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id)

        assert resp.status_code == 502
        listing = client.get(
            f"/api/animals/{animal_id}/assessments", headers=_auth()
        )
        assert listing.get_json()["data"] == []

    def test_transcription_error_returns_502(self, app, client):
        app.voice_service = _voice_service(_RaisingSTTProvider(TranscriptionError("boom")))
        animal_id = _seed_animal(app)
        resp = _post_voice(client, animal_id)

        assert resp.status_code == 502
        body = resp.get_json()
        assert body["success"] is False
        assert "currently unavailable" in body["message"]


# ---------------------------------------------------------------------------
# 4. Endpoint tests — GET /api/animals/<animal_id>/assessments/<assessment_id>/speech
# ---------------------------------------------------------------------------

def _create_voice_assessment(app, client):
    """POST a voice assessment; return (animal_id, assessment record)."""
    animal_id = _seed_animal(app)
    created = _post_voice(client, animal_id)
    assert created.status_code == 200
    return animal_id, created.get_json()["data"]["assessment"]


def _get_speech(client, animal_id, assessment_id, auth=None):
    return client.get(
        f"/api/animals/{animal_id}/assessments/{assessment_id}/speech",
        headers=auth if auth is not None else _auth(),
    )


class TestAssessmentSpeechEndpoint:
    def test_returns_wav_speaking_the_urdu_guidance(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)
        tts = _RecordingTTSProvider()
        app.voice_service = _voice_service(_FakeSTTProvider(), tts)

        resp = _get_speech(client, animal_id, assessment["id"])

        assert resp.status_code == 200
        assert resp.content_type == "audio/wav"
        assert resp.data[:4] == b"RIFF"  # recognizable WAV container
        with wave.open(io.BytesIO(resp.data)) as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == TTS_SAMPLE_RATE
            assert wav_file.readframes(wav_file.getnframes()) == tts.pcm

        # Every Urdu guidance step is spoken, in order, newline-separated.
        expected_text = "\n".join(
            assessment["diagnosis_result"]["safe_next_steps_urdu"]
        )
        assert tts.spoken_texts == [expected_text]
        assert expected_text.startswith("اگلے ایک یا دو دن میں")  # medium tier

    def test_no_auth_returns_401(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)
        resp = _get_speech(client, animal_id, assessment["id"], auth={})
        assert resp.status_code == 401

    def test_unknown_animal_returns_404(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)
        resp = _get_speech(client, "no-such-animal", assessment["id"])
        assert resp.status_code == 404

    def test_other_users_animal_returns_404(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)  # owner: user 1
        resp = _get_speech(
            client, animal_id, assessment["id"],
            auth=_auth(user_id=2, email="other@example.com"),
        )
        assert resp.status_code == 404

    def test_unknown_assessment_returns_404(self, app, client):
        animal_id, _ = _create_voice_assessment(app, client)
        resp = _get_speech(client, animal_id, "999999")
        assert resp.status_code == 404

    def test_assessment_of_different_animal_returns_404(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)
        other_animal_id = _seed_animal(app)

        resp = _get_speech(client, other_animal_id, assessment["id"])

        assert resp.status_code == 404

    @pytest.mark.parametrize("diagnosis", [
        None,  # pending record, no diagnosis yet
        {"possible_conditions": ["Something"]},  # legacy record without guidance
    ])
    def test_assessment_without_urdu_guidance_returns_404(
        self, app, client, diagnosis
    ):
        animal_id = _seed_animal(app)
        with app.app_context():
            legacy = app.health_assessment_repo.create({
                "animal_id": animal_id,
                "symptoms": "Record from before speech guidance existed.",
                "status": "completed",
                "diagnosis_result": diagnosis,
            })

        resp = _get_speech(client, animal_id, legacy["id"])

        assert resp.status_code == 404
        assert "not available" in resp.get_json()["message"]

    def test_tts_failure_returns_502(self, app, client):
        animal_id, assessment = _create_voice_assessment(app, client)
        app.voice_service = _voice_service(
            _FakeSTTProvider(),
            _RaisingTTSProvider(SpeechSynthesisError("boom")),
        )

        resp = _get_speech(client, animal_id, assessment["id"])

        assert resp.status_code == 502
        body = resp.get_json()
        assert body["success"] is False
        assert "currently unavailable" in body["message"]

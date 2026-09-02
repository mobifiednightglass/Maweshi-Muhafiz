"""
Voice service — Urdu speech-to-text and text-to-speech for symptom reporting.

Defines provider-independent ``SpeechToTextProvider`` and
``TextToSpeechProvider`` interfaces so the concrete AI backend (Gemini
today, potentially others tomorrow) can be swapped without touching the
service layer — mirroring the ``VisionAssessmentProvider`` pattern used by
the image health assessments.

* ``GeminiSpeechToTextProvider`` sends an audio recording of a farmer
  speaking in Urdu to Gemini and returns the verbatim Urdu transcript.
* ``GeminiTextToSpeechProvider`` sends Urdu text to Gemini's TTS model and
  returns raw PCM audio samples.

``VoiceService`` orchestrates the providers: it resolves the audio MIME
type, treats empty / ``NO_SPEECH_DETECTED`` model answers as a typed
``NoSpeechDetectedError``, and wraps raw PCM output into a playable WAV
container.  Failures surface as typed exceptions (``AudioFormatError``,
``TranscriptionError``, ``SpeechSynthesisError``) that the route layer
maps to HTTP status codes.

Usage:
    from app.services.voice_service import (
        GeminiSpeechToTextProvider, GeminiTextToSpeechProvider, VoiceService,
    )

    service = VoiceService(
        GeminiSpeechToTextProvider(api_key=...),
        GeminiTextToSpeechProvider(api_key=...),
    )
    transcript = service.transcribe_urdu_audio(audio_bytes, "note.mp4", "audio/mp4")
    wav_bytes  = service.urdu_text_to_speech(transcript)
"""

import io
import logging
import mimetypes
import wave
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Sentinel the model is instructed to reply with when the audio contains
# no understandable speech (see _STT_PROMPT below).
NO_SPEECH_DETECTED = "NO_SPEECH_DETECTED"

# WhatsApp voice notes are audio-only recordings inside an MP4 container,
# and browser MediaRecorder recordings arrive in a WebM container.  Both
# upload with a video/* (or generic) content type, and Windows' mimetypes
# registry also reports them as video, so these extensions are special-cased
# to the audio MIME type the speech model expects.
_AUDIO_CONTAINER_EXTENSIONS = {".mp4": "audio/mp4", ".m4a": "audio/mp4", ".webm": "audio/webm"}

# Canned transcript returned by the stub provider wired in testing mode.
# Deliberately neutral (matches no red-flag keyword).
TESTING_TRANSCRIPTION = "جانور کھانا نہیں کھا رہا اور کمزور لگتا ہے"

# Gemini TTS always returns 24,000 samples per second.
TTS_SAMPLE_RATE = 24000


# ---------------------------------------------------------------------------
# Typed exceptions — routes catch these and map them to HTTP status codes
# ---------------------------------------------------------------------------

class AudioFormatError(Exception):
    """The uploaded file is not a recognisable audio format."""


class NoSpeechDetectedError(Exception):
    """The audio contained no understandable speech to transcribe."""


class TranscriptionError(Exception):
    """The speech-to-text provider failed (network, quota, key, ...)."""


class SpeechSynthesisError(Exception):
    """The text-to-speech provider failed or returned no audio."""


# ---------------------------------------------------------------------------
# Audio MIME-type resolution
# ---------------------------------------------------------------------------

def resolve_audio_mime_type(
    filename: str | None,
    content_type: str | None = None,
) -> str:
    """Resolve the MIME type for an uploaded audio file.

    Priority:
      1. An explicit ``audio/*`` content type from the multipart upload.
      2. Voice-note container extensions (``.mp4`` / ``.m4a`` / ``.webm``)
         → their audio MIME type (``mimetypes`` would report them as
         ``video/*``).
      3. ``mimetypes`` guessing from the filename extension.

    Raises ``AudioFormatError`` when nothing recognisable is found.
    """
    normalized_type = (content_type or "").split(";")[0].strip().lower()
    if normalized_type.startswith("audio/"):
        return normalized_type

    suffix = Path(filename or "").suffix.lower()
    if suffix in _AUDIO_CONTAINER_EXTENSIONS:
        return _AUDIO_CONTAINER_EXTENSIONS[suffix]

    guessed_type, _ = mimetypes.guess_type(filename or "")
    if guessed_type and guessed_type.startswith("audio/"):
        return guessed_type

    raise AudioFormatError(
        f"Unrecognised audio format for '{filename}'. "
        "Supported formats include: .wav .mp3 .mp4 .m4a .ogg .flac .aac .webm"
    )


# ---------------------------------------------------------------------------
# Abstract provider interfaces
# ---------------------------------------------------------------------------

class SpeechToTextProvider(ABC):
    """Provider-independent interface for Urdu speech-to-text."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        """Transcribe Urdu speech and return the transcript text.

        Returns ``NO_SPEECH_DETECTED`` when the audio contains no
        understandable speech.
        """


class TextToSpeechProvider(ABC):
    """Provider-independent interface for Urdu text-to-speech."""

    @abstractmethod
    def synthesize_speech(self, text: str) -> bytes:
        """Convert Urdu text to raw PCM audio samples (16-bit mono)."""


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

# Asking for a *verbatim* transcription keeps the model from summarising or
# translating; asking for Urdu script keeps the output in the language the
# farmer actually spoke.  The sentinel keeps "no speech" machine-checkable.
_STT_PROMPT = (
    "This audio contains a farmer speaking in Urdu. "
    "Transcribe the speech verbatim, in Urdu script. "
    "Do not translate, summarise, or add commentary. "
    "If the audio contains no understandable speech, "
    f"reply with exactly: {NO_SPEECH_DETECTED}"
)

# Natural-language coaching for HOW the text is spoken (an instruction to
# the model, not text to be spoken).  "Read aloud in Urdu:" is appended by
# the provider to reinforce the output language.
_TTS_STYLE_PROMPT = "Speak in a calm, clear, and friendly tone."


# ---------------------------------------------------------------------------
# Google Gemini implementations
# ---------------------------------------------------------------------------

_DEFAULT_STT_MODEL = "gemini-3.5-flash-lite"
_DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"
_DEFAULT_TTS_VOICE = "Kore"


class GeminiSpeechToTextProvider(SpeechToTextProvider):
    """Google Gemini (google-genai SDK) speech-to-text provider.

    Parameters
    ----------
    api_key : str
        Google API key with Gemini access (read from ``GEMINI_API_KEY``).
    model : str
        Gemini model identifier.  Defaults to ``gemini-3.5-flash-lite``
        (Flash-Lite: accepts audio just like the full Flash model but has a
        far more generous free-tier daily quota).
    """

    def __init__(self, api_key: str, model: str = _DEFAULT_STT_MODEL):
        # Lazy import keeps the module importable without google-genai
        # (e.g. during unit-test setup).
        from google import genai  # noqa: WPS433
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def transcribe(self, audio_bytes: bytes, mime_type: str) -> str:
        """Send the audio to Gemini and return the transcript text.

        Raises ``TranscriptionError`` on any API / network / quota failure.
        Returns ``""`` when the response carries no readable text.
        """
        from google.genai import types  # noqa: WPS433

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[audio_part, _STT_PROMPT],
            )
        except Exception as exc:
            logger.exception("Gemini speech-to-text call failed: %s", exc)
            raise TranscriptionError(f"Speech transcription failed: {exc}") from exc

        try:
            return response.text or ""
        except Exception:
            logger.warning("Gemini response carried no readable text.")
            return ""


class GeminiTextToSpeechProvider(TextToSpeechProvider):
    """Google Gemini (google-genai SDK) text-to-speech provider.

    Parameters
    ----------
    api_key : str
        Google API key with Gemini access (read from ``GEMINI_API_KEY``).
    model : str
        Gemini TTS model identifier.  Defaults to
        ``gemini-2.5-flash-preview-tts`` — there is no Flash-Lite TTS
        variant, so this stays on the dedicated speech-generation tier.
    voice_name : str
        Prebuilt voice (all voices are multilingual and can speak Urdu).
        Options include Kore, Puck, Zephyr, Charon, Fenrir, Leda, Orus, Aoede.
    """

    def __init__(
        self,
        api_key: str,
        model: str = _DEFAULT_TTS_MODEL,
        voice_name: str = _DEFAULT_TTS_VOICE,
    ):
        from google import genai  # noqa: WPS433
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._voice = voice_name

    def synthesize_speech(self, text: str) -> bytes:
        """Send the text to Gemini's TTS model and return raw PCM samples.

        Raises ``SpeechSynthesisError`` on any API failure or when the
        response carries no audio.
        """
        from google.genai import types  # noqa: WPS433

        prompt = f"{_TTS_STYLE_PROMPT} Read aloud in Urdu: {text}"

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    # Without this the model would answer with plain text.
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self._voice,
                            ),
                        ),
                    ),
                ),
            )
        except Exception as exc:
            logger.exception("Gemini text-to-speech call failed: %s", exc)
            raise SpeechSynthesisError(f"Speech synthesis failed: {exc}") from exc

        try:
            audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        except (IndexError, AttributeError):
            audio_bytes = None

        if not audio_bytes:
            raise SpeechSynthesisError(
                "Gemini returned no audio data. The text may have been refused."
            )
        return audio_bytes


# ---------------------------------------------------------------------------
# PCM → WAV wrapping
# ---------------------------------------------------------------------------

def wrap_pcm_as_wav(pcm_bytes: bytes, sample_rate: int = TTS_SAMPLE_RATE) -> bytes:
    """Wrap raw 16-bit mono PCM samples into a playable WAV container.

    A WAV file is the same sample stream plus a small header saying "this
    is 16-bit mono audio at ``sample_rate``".  Using ``BytesIO`` lets the
    stdlib ``wave`` module build the file entirely in memory.
    """
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)            # mono (one speaker)
        wav_file.setsampwidth(2)            # 2 bytes = 16-bit samples
        wav_file.setframerate(sample_rate)  # samples per second
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class VoiceService:
    """Orchestrates Urdu speech-to-text and text-to-speech.

    Delegates the AI calls to the injected providers and adds the
    upload-level concerns the routes should not have to know about:
    MIME-type resolution, empty / no-speech handling, and WAV wrapping.
    """

    def __init__(
        self,
        stt_provider: SpeechToTextProvider,
        tts_provider: TextToSpeechProvider,
    ):
        self._stt = stt_provider
        self._tts = tts_provider

    # ------------------------------------------------------------------
    # Speech → text
    # ------------------------------------------------------------------

    def transcribe_urdu_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> str:
        """Transcribe an uploaded Urdu voice recording into text.

        Raises
        ------
        AudioFormatError
            The upload is empty or not a recognisable audio format.
        NoSpeechDetectedError
            The model found no understandable speech.
        TranscriptionError
            The provider call failed.
        """
        if not audio_bytes:
            raise AudioFormatError("The uploaded audio file is empty.")

        mime_type = resolve_audio_mime_type(filename, content_type)

        try:
            transcript = self._stt.transcribe(audio_bytes, mime_type)
        except TranscriptionError:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in speech-to-text provider: %s", exc)
            raise TranscriptionError(f"Speech transcription failed: {exc}") from exc

        transcript = (transcript or "").strip()
        if not transcript or transcript == NO_SPEECH_DETECTED:
            raise NoSpeechDetectedError(
                "No understandable speech was detected in the audio."
            )
        return transcript

    # ------------------------------------------------------------------
    # Text → speech
    # ------------------------------------------------------------------

    def urdu_text_to_speech(self, text: str) -> bytes:
        """Convert Urdu text into a complete WAV file's bytes.

        Raises ``SpeechSynthesisError`` when the text is empty or the
        provider fails.
        """
        text = (text or "").strip()
        if not text:
            raise SpeechSynthesisError("The input text is empty — nothing to speak.")

        try:
            pcm_bytes = self._tts.synthesize_speech(text)
        except SpeechSynthesisError:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in text-to-speech provider: %s", exc)
            raise SpeechSynthesisError(f"Speech synthesis failed: {exc}") from exc

        if not pcm_bytes:
            raise SpeechSynthesisError("The speech provider returned no audio data.")

        return wrap_pcm_as_wav(pcm_bytes)

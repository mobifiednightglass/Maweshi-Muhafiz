"""
Standalone Urdu speech-to-text script (NOT connected to the Flask app).

Takes the path to an audio file (e.g. a farmer describing their animal's
symptoms in Urdu), sends the audio to Google Gemini, and prints the
transcribed Urdu text.

Why Gemini (google-genai) instead of Google Cloud Speech-to-Text?
    The project already has the ``google-genai`` package installed and a
    working GEMINI_API_KEY (used for the image health assessments).
    Gemini is multimodal — it accepts audio directly — so we need no new
    packages, no Google Cloud project, and no service-account file.
    Google Cloud Speech-to-Text would require all three.

How to run (from anywhere, using the backend's virtual environment):

    C:/.../Maweshi-Muhafiz/backend/venv/Scripts/python.exe ^
        C:/.../Maweshi-Muhafiz/voice_scripts/speech_to_text.py my_recording.wav

Requirements (already satisfied by backend/requirements.txt):
    - google-genai      (talks to Gemini)
    - python-dotenv     (loads GEMINI_API_KEY from backend/.env)
"""

import io
import mimetypes
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# STEP 0 — Make the Windows console able to print Urdu text.
#
# Urdu uses a non-Latin script, but the Windows console defaults to an old
# encoding (cp1252) that cannot display it.  Re-wrapping stdout in UTF-8
# prevents a UnicodeEncodeError crash when we print the transcription.
# This must happen BEFORE any Urdu text is printed.
# ---------------------------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# STEP 1 — Load the API key from the backend .env file.
#
# The key lives in backend/.env as GEMINI_API_KEY=...  We load it into the
# process environment here so the script works no matter which folder you
# run it from.  (The key itself is never printed.)
# ---------------------------------------------------------------------------
def _load_api_key() -> str:
    from dotenv import load_dotenv  # part of python-dotenv

    # Look for the .env file in the two most likely places:
    #   1. backend/.env      (next to voice_scripts — the normal project layout)
    #   2. the current working directory (fallback)
    script_dir = Path(__file__).resolve().parent
    candidate_paths = [
        script_dir.parent / "backend" / ".env",
        Path.cwd() / ".env",
    ]

    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break

    import os

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        # Stop with a helpful message instead of a cryptic auth error later.
        sys.exit(
            "ERROR: GEMINI_API_KEY is not set.\n"
            "Make sure backend/.env contains a line like:  GEMINI_API_KEY=your-key"
        )
    return api_key


# ---------------------------------------------------------------------------
# STEP 2 — Work out the audio file's MIME type from its extension.
#
# Gemini needs to be told what kind of audio it is receiving
# (e.g. "audio/wav" or "audio/mpeg").  Python's built-in mimetypes
# module maps file extensions to MIME types for us.
# ---------------------------------------------------------------------------
# WhatsApp voice notes are audio-only recordings stored in an MP4 container
# with a ".mp4" extension.  Python's mimetypes module would report those as
# "video/mp4", so we special-case the extension and send the audio MIME
# type Gemini expects for audio inside an MP4 container.
_WHATSAPP_AUDIO_EXTENSIONS = {".mp4"}


def _audio_mime_type(file_path: Path) -> str:
    if file_path.suffix.lower() in _WHATSAPP_AUDIO_EXTENSIONS:
        return "audio/mp4"

    mime_type, _ = mimetypes.guess_type(file_path.name)
    if not mime_type or not mime_type.startswith("audio/"):
        sys.exit(
            f"ERROR: Unrecognised audio format for '{file_path.name}'.\n"
            "Supported formats include: .wav  .mp3  .mp4  .m4a  .ogg  .flac  .aac  .webm"
        )
    return mime_type


# ---------------------------------------------------------------------------
# STEP 3 — Send the audio to Gemini and get the transcription back.
#
# This is the core function.  It:
#   a) reads the audio file's raw bytes,
#   b) wraps them in a "Part" object (how the SDK packages file data),
#   c) sends them to Gemini together with a text prompt that says
#      "transcribe this Urdu speech", and
#   d) returns the model's text answer.
# ---------------------------------------------------------------------------
def transcribe_urdu_audio(audio_path: str) -> str:
    from google import genai
    from google.genai import types

    file_path = Path(audio_path)
    if not file_path.exists():
        sys.exit(f"ERROR: Audio file not found: {file_path}")

    # (a) Read the raw bytes of the audio file.
    audio_bytes = file_path.read_bytes()
    if not audio_bytes:
        sys.exit(f"ERROR: Audio file is empty: {file_path}")

    # (b) Package the audio for the API.  mime_type tells Gemini the format.
    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=_audio_mime_type(file_path),
    )

    # (c) The instruction that goes alongside the audio.
    #     Asking for a *verbatim* transcription keeps the model from
    #     summarising or translating; asking for Urdu script keeps the
    #     output in the language the farmer actually spoke.
    prompt = (
        "This audio contains a farmer speaking in Urdu. "
        "Transcribe the speech verbatim, in Urdu script. "
        "Do not translate, summarise, or add commentary. "
        "If the audio contains no understandable speech, "
        "reply with exactly: NO_SPEECH_DETECTED"
    )

    # Build the API client using the key loaded from backend/.env.
    client = genai.Client(api_key=_load_api_key())

    # Flash-Lite model (same one the health assessments use): it accepts
    # audio just like the full Flash model but has a far more generous
    # free-tier daily quota.
    model = "gemini-3.5-flash-lite"

    # (d) Call Gemini: contents = [the audio, the instruction].
    #     Any API failure (bad key, no network, quota exhausted, ...) is
    #     converted into a clear one-line error instead of a long traceback.
    try:
        response = client.models.generate_content(
            model=model,
            contents=[audio_part, prompt],
        )
    except Exception as exc:
        sys.exit(
            f"ERROR: The Gemini API call failed: {exc}\n"
            "Common causes: no internet, an invalid GEMINI_API_KEY, or the "
            "free-tier daily quota being used up (try again tomorrow or "
            "enable billing at https://ai.google.dev)."
        )
    return response.text


# ---------------------------------------------------------------------------
# STEP 4 — Command-line entry point.
#
# Usage:  python speech_to_text.py <path-to-audio-file>
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(
            "Usage: python speech_to_text.py <path-to-audio-file>\n"
            "Example: python speech_to_text.py C:/recordings/goat_symptoms.wav"
        )

    audio_path = sys.argv[1]
    transcription = transcribe_urdu_audio(audio_path)

    print("----- Transcription (Urdu) -----")
    print(transcription)
    print("--------------------------------")


if __name__ == "__main__":
    # Running the file directly (e.g. `python speech_to_text.py my.wav`)
    # executes main(); importing it from another script does not.
    main()

    # ------------------------------------------------------------------
    # Example — calling the transcription function from other Python code:
    #
    #     from speech_to_text import transcribe_urdu_audio
    #
    #     text = transcribe_urdu_audio("C:/recordings/goat_symptoms.wav")
    #     print(text)   # -> the Urdu transcription, ready for further use
    # ------------------------------------------------------------------

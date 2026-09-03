"""
Standalone Urdu text-to-speech script (NOT connected to the Flask app).

Takes Urdu text (given on the command line or in a .txt file), sends it to
Google Gemini's text-to-speech model, and saves the spoken audio as a WAV
file you can play anywhere.

Why WAV and not MP3?
    Gemini's TTS model returns raw, uncompressed audio samples (PCM data).
    Python's built-in ``wave`` module can wrap those samples into a
    standard WAV file with zero extra packages.  Creating an MP3 instead
    would require installing an external encoder (e.g. ffmpeg), which is
    not in the project's requirements.

How to run (from anywhere, using the backend's virtual environment):

    C:/.../Maweshi-Muhafiz/backend/venv/Scripts/python.exe ^
        C:/.../Maweshi-Muhafiz/voice_scripts/text_to_speech.py "جملہ یہاں لکھیں"

Requirements (already satisfied by backend/requirements.txt):
    - google-genai      (talks to Gemini)
    - python-dotenv     (loads GEMINI_API_KEY from backend/.env)
"""

import io
import sys
import wave
from pathlib import Path

# ---------------------------------------------------------------------------
# STEP 0 — Make the Windows console able to print Urdu text.
#
# Urdu uses a non-Latin script, but the Windows console defaults to an old
# encoding (cp1252) that cannot display it.  Re-wrapping stdout in UTF-8
# prevents a crash if we ever echo Urdu text (e.g. an input preview).
# ---------------------------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# STEP 1 — Load the API key from the backend .env file.
#
# Same key and same loading logic as speech_to_text.py: GEMINI_API_KEY is
# stored in backend/.env, and the key itself is never printed.
# ---------------------------------------------------------------------------
def _load_api_key() -> str:
    from dotenv import load_dotenv  # part of python-dotenv

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
        sys.exit(
            "ERROR: GEMINI_API_KEY is not set.\n"
            "Make sure backend/.env contains a line like:  GEMINI_API_KEY=your-key"
        )
    return api_key


# ---------------------------------------------------------------------------
# STEP 2 — Settings you can safely change.
#
# VOICE_NAME: Gemini TTS offers several prebuilt voices (all are
#     multilingual, so they can all speak Urdu).  Options include:
#     Kore, Puck, Zephyr, Charon, Fenrir, Leda, Orus, Aoede.
# STYLE_PROMPT: optional natural-language coaching for HOW the text is
#     spoken.  Change to "" to remove it.  (Keep it in English — it is an
#     instruction to the model, not text to be spoken.)
# SAMPLE_RATE: Gemini TTS always returns audio at 24,000 samples per
#     second.  Do not change this unless Google's docs say otherwise.
# TTS_MODEL: a dedicated speech-generation model (it needs the AUDIO
#     output mode used below).  Unlike the transcription and vision calls
#     in this project, there is no Flash-Lite TTS model (checked
#     2026-09-03), so this stays on the Flash TTS tier.
# ---------------------------------------------------------------------------
VOICE_NAME = "Kore"
STYLE_PROMPT = "Speak in a calm, clear, and friendly tone."
SAMPLE_RATE = 24000
TTS_MODEL = "gemini-2.5-flash-preview-tts"


# ---------------------------------------------------------------------------
# STEP 3 — Send the Urdu text to Gemini and get raw audio back.
#
# This is the core function.  It:
#   a) combines the style instruction with the Urdu text,
#   b) asks Gemini's TTS model to generate speech (response_modalities
#      tells the API we want AUDIO back, not text),
#   c) digs the raw audio bytes out of the response.
# ---------------------------------------------------------------------------
def synthesize_urdu_speech(text: str) -> bytes:
    from google import genai
    from google.genai import types

    # (a) The model can take style instructions in the same prompt as the
    #     text to speak.  "Read aloud in Urdu:" also reinforces which
    #     language we want, even when the text is short.
    full_prompt = f"{STYLE_PROMPT} Read aloud in Urdu: {text}" if STYLE_PROMPT else text

    client = genai.Client(api_key=_load_api_key())

    # (b) Ask for audio output.  If any part of this fails (bad key, no
    #     network, daily quota used up, ...), exit with one clear line
    #     instead of a long SDK traceback.
    try:
        response = client.models.generate_content(
            model=TTS_MODEL,
            contents=[full_prompt],
            config=types.GenerateContentConfig(
                # Without this the model would answer with plain text.
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=VOICE_NAME,
                        ),
                    ),
                ),
            ),
        )
    except Exception as exc:
        sys.exit(
            f"ERROR: The Gemini API call failed: {exc}\n"
            "Common causes: no internet, an invalid GEMINI_API_KEY, or the "
            "free-tier daily quota being used up (try again tomorrow or "
            "enable billing at https://ai.google.dev)."
        )

    # (c) The audio comes back as "inline data" attached to the first
    #     candidate's first part.  The SDK has already base64-decoded it
    #     into raw bytes for us.
    try:
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
    except (IndexError, AttributeError):
        sys.exit(
            "ERROR: Gemini returned no audio.\n"
            "The text may have been refused or empty.  Try different input text."
        )

    if not audio_bytes:
        sys.exit("ERROR: Gemini returned empty audio data.  Try different input text.")

    return audio_bytes


# ---------------------------------------------------------------------------
# STEP 4 — Wrap the raw audio bytes into a playable WAV file.
#
# Gemini TTS returns uncompressed PCM samples: just a long stream of
# 16-bit numbers, one per audio "tick", with no header.  A WAV file is the
# same stream plus a small header saying "this is 16-bit mono audio at
# SAMPLE_RATE".  Python's built-in wave module writes that header for us.
# ---------------------------------------------------------------------------
def save_as_wav(pcm_bytes: bytes, output_path: Path) -> Path:
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)          # mono (one speaker)
        wav_file.setsampwidth(2)          # 2 bytes = 16-bit samples
        wav_file.setframerate(SAMPLE_RATE)  # samples per second
        wav_file.writeframes(pcm_bytes)
    return output_path


# ---------------------------------------------------------------------------
# STEP 5 — Convert Urdu text to a WAV file (main entry point).
#
# Returns the Path of the WAV file that was written.
# ---------------------------------------------------------------------------
def urdu_text_to_speech(text: str, output_path: str | None = None) -> Path:
    text = text.strip()
    if not text:
        sys.exit("ERROR: The input text is empty — nothing to speak.")

    # Default output name: speech_output.wav next to this script.
    out_path = Path(output_path) if output_path else Path("speech_output.wav")
    out_path = out_path.with_suffix(".wav")

    pcm_bytes = synthesize_urdu_speech(text)
    save_as_wav(pcm_bytes, out_path)
    return out_path


# ---------------------------------------------------------------------------
# STEP 6 — Command-line entry point.
#
# Usage:  python text_to_speech.py <urdu-text-or-txt-file> [output.wav]
#
# The first argument can be either the Urdu text itself (in quotes) or the
# path of a .txt file containing Urdu text (useful because typing Urdu in
# the Windows console is awkward).
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(
            "Usage: python text_to_speech.py <urdu-text-or-txt-file> [output.wav]\n"
            "Examples:\n"
            '  python text_to_speech.py "جانور کو سانس لینے میں دشواری ہے"\n'
            "  python text_to_speech.py symptoms.txt my_audio.wav"
        )

    text_arg = sys.argv[1]
    output_arg = sys.argv[2] if len(sys.argv) > 2 else None

    # If the argument names an existing file, read the Urdu text from it.
    candidate = Path(text_arg)
    if candidate.exists() and candidate.suffix.lower() == ".txt":
        text = candidate.read_text(encoding="utf-8")
        # Default output next to the input file: symptoms.txt -> symptoms.wav
        if output_arg is None:
            output_arg = str(candidate.with_suffix(".wav"))
    else:
        text = text_arg

    wav_path = urdu_text_to_speech(text, output_arg)
    print(f"Saved spoken audio to: {wav_path}")


if __name__ == "__main__":
    # Running the file directly executes main(); importing does not.
    main()

    # ------------------------------------------------------------------
    # Example — calling from other Python code:
    #
    #     from text_to_speech import urdu_text_to_speech
    #
    #     wav = urdu_text_to_speech(
    #         "جانور کو سانس لینے میں دشواری ہے",
    #         output_path="breathing_difficulty.wav",
    #     )
    #     print(wav)   # -> Path of the saved audio file
    # ------------------------------------------------------------------

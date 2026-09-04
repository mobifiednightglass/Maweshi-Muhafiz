"""
Vision-assessment provider abstraction and Google Gemini implementation.

Defines a provider-independent ``VisionAssessmentProvider`` interface so the
concrete AI backend (Gemini today, potentially others tomorrow) can be
swapped without touching the service layer.

The ``GeminiVisionProvider`` sends an image + symptoms text to Google
Gemini's vision-capable model and parses the response into a structured
diagnosis dict.  On any failure the caller always receives a safe fallback
dict — unhandled exceptions never propagate.

Usage:
    from app.services.vision_provider import GeminiVisionProvider

    provider = GeminiVisionProvider(api_key=os.environ["GEMINI_API_KEY"])
    result   = provider.assess(image_bytes, "image/jpeg", "Swollen leg, limping")
"""

import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Structured-response field contract
# ---------------------------------------------------------------------------

REQUIRED_RESULT_FIELDS = frozenset({
    "possible_conditions",
    "explanation",
    "confidence_note",
    "urgency_level",
})

VALID_URGENCY_LEVELS = frozenset({"low", "medium", "high"})

# Thinking budget for Gemini calls (lower = faster, but may reduce quality).
# Tune this if diagnosis quality suffers or response time is too slow.
_THINKING_BUDGET = 512

# Unicode range for Devanagari script (Hindi).  Used as a safety net to
# detect when the AI returns Hindi instead of Urdu in _urdu fields.
_DEVANAGARI_RANGE = range(0x0900, 0x0980)

# Safe Urdu fallback text used when Devanagari is detected in a _urdu field.
_URDU_FALLBACK_EXPLANATION = (
    "خودکار تصویری تشخیص کا نتیجہ دستیاب نہیں ہو سکا۔ "
    "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
)
_URDU_FALLBACK_CONFIDENCE = (
    "خودکار تشخیص مکمل نہیں ہو سکی۔ "
    "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
)
_URDU_FALLBACK_CONDITIONS = ["حالت کی تشخیص دستیاب نہیں"]


def _contains_devanagari(text: str) -> bool:
    """Return True if *text* contains any Devanagari (Hindi) characters."""
    return any(ord(ch) in _DEVANAGARI_RANGE for ch in text)


# ---------------------------------------------------------------------------
# Safe fallback — returned whenever the AI call or parsing fails
# ---------------------------------------------------------------------------

def safe_fallback(reason: str | None = None) -> dict:
    """Return a safe, conservative assessment dict.

    Used as a last-resort result when the AI provider is unreachable or
    returns unparseable output.  Always flags ``urgency_level`` as
    ``"medium"`` and recommends manual vet review.
    Includes both English and Urdu fields.
    """
    note = (
        "Automated assessment could not be completed. "
        "Manual veterinary review is strongly recommended."
    )
    note_urdu = (
        "خودکار تشخیص مکمل نہیں ہو سکی۔ "
        "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
    )
    if reason:
        note = f"{note} Reason: {reason}"
    return {
        "possible_conditions": [],
        "explanation": (
            "The automated vision assessment was unable to produce a result. "
            "A qualified veterinarian should examine the animal."
        ),
        "confidence_note": note,
        "urgency_level": "medium",
        "image_too_blurry": False,
        "contains_animal": True,
        # Urdu translations
        "possible_conditions_urdu": [],
        "explanation_urdu": (
            "خودکار تصویری تشخیص کا نتیجہ دستیاب نہیں ہو سکا۔ "
            "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
        ),
        "confidence_note_urdu": note_urdu,
    }


# ---------------------------------------------------------------------------
# Abstract provider interface
# ---------------------------------------------------------------------------

class VisionAssessmentProvider(ABC):
    """Provider-independent interface for vision-based health assessment."""

    @abstractmethod
    def assess(
        self,
        image_bytes: bytes,
        image_content_type: str,
        symptoms: str,
    ) -> dict:
        """Analyse an image + symptoms description.

        Returns a dict with keys: ``possible_conditions`` (list[str]),
        ``explanation`` (str), ``confidence_note`` (str), and
        ``urgency_level`` ("low" | "medium" | "high").
        """


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = (
    "You are a veterinary AI assistant. You provide preliminary health "
    "assessments for livestock based on photos and symptom descriptions. "
    "You are NOT a substitute for professional veterinary diagnosis. "
    "Always acknowledge uncertainty and recommend consulting a qualified "
    "veterinarian. "
    "You must respond in both English and Urdu. "
    "CRITICAL LANGUAGE RULE FOR URDU: All Urdu text MUST be written in "
    "the Urdu/Arabic script (Nastaliq style). You MUST NOT use Hindi or "
    "Devanagari script under any circumstances. Use natural, simple "
    "Pakistani Urdu that an ordinary Pakistani farmer can easily "
    "understand. Keep medical and animal-health terminology clear and "
    "appropriate for a rural Pakistani audience. "
    "For high-urgency or emergency cases, the Urdu explanation and "
    "confidence note must clearly communicate that immediate veterinary "
    "attention is required. "
    "Do not include treatment instructions or medication dosages in any "
    "language."
)

_BASE_PROMPT = """\
Analyse the attached livestock photo together with the following symptoms
reported by the farmer:

\"\"\"{symptoms}\"\"\"

Return a **JSON object** with exactly these nine keys.

IMPORTANT LANGUAGE RULES:
- The fields "possible_conditions", "explanation", "confidence_note", and
  "urgency_level" MUST be written in English ONLY. Do NOT include any Urdu
  words, phrases, or script in these fields.
- The fields "explanation_urdu", "possible_conditions_urdu", and
  "confidence_note_urdu" MUST be written in Urdu ONLY, using the
  Urdu/Arabic script (Nastaliq). Do NOT use Hindi or Devanagari script.
  Use natural, simple Pakistani Urdu that a farmer can easily understand.

Keys:

- "possible_conditions": a list of strings naming plausible health conditions (English ONLY, no Urdu)
- "explanation": a brief paragraph explaining your reasoning (English ONLY, no Urdu)
- "confidence_note": a short statement about your confidence level (English ONLY, no Urdu).
  It MUST explicitly say this is an AI-assisted preliminary assessment,
  not a medical diagnosis, and that uncertainty should be acknowledged.
- "urgency_level": one of "low", "medium", or "high"
- "image_too_blurry": a boolean — true if the animal in the photo cannot be clearly seen due to blur or being out of focus, false otherwise
- "contains_animal": a boolean — true if the photo clearly shows an animal (of any species) as the main subject, false if it shows something else (a person, an object, a landscape with no animal, etc.) or if no clear animal is visible
- "explanation_urdu": the same explanation translated into natural, simple Urdu that a farmer can easily understand. Use Urdu script.
- "possible_conditions_urdu": a list of the same conditions translated into simple Urdu
- "confidence_note_urdu": the same confidence note translated into simple Urdu. If urgency is "high", clearly state in Urdu that فوری طور پر ڈاکٹر (ویٹرنری) سے رجوع کرنا ضروری ہے (immediate veterinary attention is required).
"""

_STRICT_PROMPT = """\
You MUST respond with ONLY a valid JSON object — no markdown, no prose
before or after the JSON.

Analyse the attached livestock photo and the following symptoms:

\"\"\"{symptoms}\"\"\"

LANGUAGE RULES:
- "possible_conditions", "explanation", "confidence_note" MUST be in English ONLY. No Urdu text.
- "explanation_urdu", "possible_conditions_urdu", "confidence_note_urdu" MUST be in Urdu/Arabic script ONLY. Do NOT use Hindi or Devanagari script. Use simple Pakistani Urdu.

Return this exact JSON structure:

{{
  "possible_conditions": ["condition 1", "condition 2"],
  "explanation": "Your reasoning here in English only. No Urdu.",
  "confidence_note": "State in English only that this is an AI-assisted preliminary assessment, not a diagnosis, and acknowledge uncertainty.",
  "urgency_level": "low" | "medium" | "high",
  "image_too_blurry": true | false,
  "contains_animal": true | false,
  "explanation_urdu": "یہاں آسان اردو میں وضاحت لکھیں۔ اگر فوری ضرورت ہے تو واضح طور پر بتائیں کہ فوری ڈاکٹر سے ملنا ضروری ہے۔",
  "possible_conditions_urdu": ["حالت 1", "حالت 2"],
  "confidence_note_urdu": "یہاں آسان اردو میں اعتماد کی وضاحت لکھیں۔"
}}
"""


# ---------------------------------------------------------------------------
# Google Gemini implementation
# ---------------------------------------------------------------------------

_DEFAULT_MODEL = "gemini-3.5-flash-lite"


class GeminiVisionProvider(VisionAssessmentProvider):
    """Google Gemini (google-genai SDK) vision-assessment provider.

    Parameters
    ----------
    api_key : str
        Google API key with Gemini access (read from ``GEMINI_API_KEY``).
    model : str
        Gemini model identifier.  Defaults to ``gemini-3.5-flash-lite``
        (Flash-Lite: same multimodal behaviour as the full Flash model,
        but a far more generous free-tier daily quota).
    """

    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL):
        # Lazy import so the rest of the module can be imported even if
        # google-genai is not yet installed (e.g. during unit-test setup).
        from google import genai  # noqa: WPS433
        self._client = genai.Client(api_key=api_key)
        self._model = model

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def assess(
        self,
        image_bytes: bytes,
        image_content_type: str,
        symptoms: str,
    ) -> dict:
        """Call Gemini with the image + symptoms and return a structured dict.

        On a malformed response: retries once with a stricter prompt.
        On any API / network / key error: returns ``safe_fallback()``
        with the failure reason logged.
        """
        try:
            # --- First attempt (standard prompt) -------------------------
            result = self._call_gemini(image_bytes, image_content_type, symptoms)
            parsed = self._parse_response(result)
            if parsed is not None:
                return parsed

            # --- Retry with stricter prompt ------------------------------
            logger.warning(
                "First Gemini response was not parseable; retrying with "
                "stricter prompt."
            )
            result = self._call_gemini(
                image_bytes, image_content_type, symptoms, strict=True,
            )
            parsed = self._parse_response(result)
            if parsed is not None:
                return parsed

            # --- Both attempts failed ------------------------------------
            logger.error(
                "Gemini returned unparseable output after retry; "
                "returning safe fallback."
            )
            return safe_fallback(
                "AI model returned an unparseable response after two attempts."
            )

        except Exception as exc:
            logger.exception("Gemini API call failed: %s", exc)
            return safe_fallback(f"AI provider error: {exc}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_gemini(
        self,
        image_bytes: bytes,
        image_content_type: str,
        symptoms: str,
        *,
        strict: bool = False,
    ):
        """Send a multimodal request to Gemini and return the raw response."""
        from google.genai import types  # noqa: WPS433

        prompt_text = (
            _STRICT_PROMPT.format(symptoms=symptoms)
            if strict
            else _BASE_PROMPT.format(symptoms=symptoms)
        )

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_content_type,
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=[image_part, prompt_text],
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=_THINKING_BUDGET),
            ),
        )
        return response

    @staticmethod
    def _parse_response(response) -> dict | None:
        """Extract and validate the structured dict from a Gemini response.

        Returns the dict if valid, or ``None`` if parsing fails.
        """
        try:
            text = response.text
        except Exception:
            logger.debug("Could not read response.text from Gemini response.")
            return None

        if not text:
            return None

        # Try JSON parse — the model may still wrap it in markdown
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Attempt to extract JSON from markdown code blocks
            import re
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                except json.JSONDecodeError:
                    return None
            else:
                return None

        if not isinstance(data, dict):
            return None

        # Check all required fields are present
        if not REQUIRED_RESULT_FIELDS.issubset(data.keys()):
            return None

        # Normalise urgency_level
        urgency = data.get("urgency_level", "")
        if not isinstance(urgency, str) or urgency.lower() not in VALID_URGENCY_LEVELS:
            data["urgency_level"] = "medium"
        else:
            data["urgency_level"] = urgency.lower()

        # Ensure possible_conditions is a list
        if not isinstance(data["possible_conditions"], list):
            data["possible_conditions"] = [str(data["possible_conditions"])]

        # Populate optional Urdu fields with safe defaults when absent
        # (keeps the API response shape consistent for all clients)
        data.setdefault("explanation_urdu", "")
        data.setdefault("possible_conditions_urdu", [])
        data.setdefault("confidence_note_urdu", "")

        # Ensure possible_conditions_urdu is a list
        if not isinstance(data["possible_conditions_urdu"], list):
            data["possible_conditions_urdu"] = [str(data["possible_conditions_urdu"])]

        # Safety net: reject Devanagari (Hindi) script in _urdu fields.
        # If any _urdu field contains Devanagari characters, replace it
        # with a safe Urdu fallback so the client never receives Hindi.
        if _contains_devanagari(data.get("explanation_urdu", "")):
            logger.warning("Devanagari detected in explanation_urdu; replacing with Urdu fallback.")
            data["explanation_urdu"] = _URDU_FALLBACK_EXPLANATION
        if _contains_devanagari(data.get("confidence_note_urdu", "")):
            logger.warning("Devanagari detected in confidence_note_urdu; replacing with Urdu fallback.")
            data["confidence_note_urdu"] = _URDU_FALLBACK_CONFIDENCE
        if any(
            _contains_devanagari(str(c))
            for c in data.get("possible_conditions_urdu", [])
        ):
            logger.warning("Devanagari detected in possible_conditions_urdu; replacing with Urdu fallback.")
            data["possible_conditions_urdu"] = _URDU_FALLBACK_CONDITIONS

        # Default image_too_blurry safely — must be a bool, default False
        blur_value = data.get("image_too_blurry")
        if not isinstance(blur_value, bool):
            data["image_too_blurry"] = False

        # Default contains_animal safely — must be a bool, default True
        # (fail open: a missing/malformed field should not block the user)
        animal_value = data.get("contains_animal")
        if not isinstance(animal_value, bool):
            data["contains_animal"] = True

        return data

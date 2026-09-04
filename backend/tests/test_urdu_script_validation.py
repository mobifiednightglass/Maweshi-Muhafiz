"""
Tests for Urdu script validation in AI-generated and server-generated fields.

Ensures that all ``_urdu`` fields contain proper Urdu/Arabic script,
never Hindi/Devanagari.  Covers:

  1. _contains_devanagari helper — detects Hindi, accepts Urdu
  2. _parse_response — replaces Devanagari with safe Urdu fallback
  3. _parse_response — preserves valid Urdu text
  4. safe_fallback — Urdu fields are Devanagari-free
  5. Prompt templates — contain the required language rules
  6. next_steps_service — server-generated Urdu is Devanagari-free
"""

import json

import pytest
from app.services.next_steps_service import (
    _EMERGENCY_STEPS_URDU,
    _LOW_STEPS_URDU,
    _MEDIUM_STEPS_URDU,
    build_safe_next_steps,
)
from app.services.vision_provider import (
    _BASE_PROMPT,
    _STRICT_PROMPT,
    _SYSTEM_INSTRUCTION,
    _contains_devanagari,
    safe_fallback,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeGeminiResponse:
    """Minimal stand-in for a Gemini response with a .text attribute."""

    def __init__(self, text):
        self.text = text


def _valid_ai_json(**overrides):
    """Build a minimal valid AI response JSON string."""
    data = {
        "possible_conditions": ["Sprain"],
        "explanation": "Mild limp visible.",
        "confidence_note": "AI-assisted preliminary assessment.",
        "urgency_level": "low",
        "image_too_blurry": False,
        "contains_animal": True,
        "explanation_urdu": "ہلکی لنگڑاہٹ نظر آ رہی ہے۔",
        "possible_conditions_urdu": ["مچکاو"],
        "confidence_note_urdu": "یہ خودکار تشخیص ہے، حتمی نہیں۔",
    }
    data.update(overrides)
    return json.dumps(data, ensure_ascii=False)


def _parse(text):
    """Call _parse_response with a fake Gemini response."""
    from app.services.vision_provider import GeminiVisionProvider
    return GeminiVisionProvider._parse_response(_FakeGeminiResponse(text))


# ---------------------------------------------------------------------------
# 1. _contains_devanagari helper
# ---------------------------------------------------------------------------

class TestContainsDevanagari:
    def test_detects_hindi_text(self):
        # Hindi: "यह जानवर बीमार है" (This animal is sick)
        assert _contains_devanagari("यह जानवर बीमार है") is True

    def test_detects_single_devanagari_char(self):
        assert _contains_devanagari("hello अ world") is True

    def test_accepts_urdu_text(self):
        assert _contains_devanagari("یہ جانور بیمار ہے") is False

    def test_accepts_english_text(self):
        assert _contains_devanagari("This is plain English.") is False

    def test_accepts_empty_string(self):
        assert _contains_devanagari("") is False

    def test_accepts_urdu_with_punctuation(self):
        assert _contains_devanagari("براہ کرم ڈاکٹر سے ملیں۔") is False


# ---------------------------------------------------------------------------
# 2. _parse_response — Devanagari replacement
# ---------------------------------------------------------------------------

class TestParseResponseDevanagariRejection:
    def test_devanagari_in_explanation_urdu_is_replaced(self):
        hindi_explanation = "यह जानवर बीमार लग रहा है।"
        result = _parse(_valid_ai_json(explanation_urdu=hindi_explanation))

        assert result is not None
        assert not _contains_devanagari(result["explanation_urdu"])
        # Should contain Urdu fallback text
        assert "خودکار" in result["explanation_urdu"]

    def test_devanagari_in_confidence_note_urdu_is_replaced(self):
        hindi_confidence = "यह एक स्वचालित मूल्यांकन है।"
        result = _parse(_valid_ai_json(confidence_note_urdu=hindi_confidence))

        assert result is not None
        assert not _contains_devanagari(result["confidence_note_urdu"])
        assert "خودکار" in result["confidence_note_urdu"]

    def test_devanagari_in_possible_conditions_urdu_is_replaced(self):
        hindi_conditions = ["सूजन", "बुखार"]
        result = _parse(_valid_ai_json(possible_conditions_urdu=hindi_conditions))

        assert result is not None
        for condition in result["possible_conditions_urdu"]:
            assert not _contains_devanagari(condition)

    def test_devanagari_in_all_urdu_fields_replaced(self):
        result = _parse(_valid_ai_json(
            explanation_urdu="हिन्दी में व्याख्या",
            confidence_note_urdu="हिन्दी में नोट",
            possible_conditions_urdu=["हिन्दी"],
        ))

        assert result is not None
        assert not _contains_devanagari(result["explanation_urdu"])
        assert not _contains_devanagari(result["confidence_note_urdu"])
        for c in result["possible_conditions_urdu"]:
            assert not _contains_devanagari(c)


# ---------------------------------------------------------------------------
# 3. _parse_response — valid Urdu is preserved
# ---------------------------------------------------------------------------

class TestParseResponsePreservesUrdu:
    def test_valid_urdu_explanation_preserved(self):
        urdu_text = "ہلکی سوجن نظر آ رہی ہے۔"
        result = _parse(_valid_ai_json(explanation_urdu=urdu_text))

        assert result is not None
        assert result["explanation_urdu"] == urdu_text

    def test_valid_urdu_conditions_preserved(self):
        urdu_conditions = ["سوجن", "بخار"]
        result = _parse(_valid_ai_json(possible_conditions_urdu=urdu_conditions))

        assert result is not None
        assert result["possible_conditions_urdu"] == urdu_conditions

    def test_valid_urdu_confidence_preserved(self):
        urdu_note = "یہ خودکار تشخیص ہے، حتمی نہیں۔"
        result = _parse(_valid_ai_json(confidence_note_urdu=urdu_note))

        assert result is not None
        assert result["confidence_note_urdu"] == urdu_note

    def test_english_fields_unaffected(self):
        result = _parse(_valid_ai_json())

        assert result is not None
        assert result["possible_conditions"] == ["Sprain"]
        assert result["explanation"] == "Mild limp visible."
        assert result["urgency_level"] == "low"


# ---------------------------------------------------------------------------
# 4. safe_fallback — Urdu fields are Devanagari-free
# ---------------------------------------------------------------------------

class TestSafeFallbackUrdu:
    def test_fallback_explanation_urdu_no_devanagari(self):
        fb = safe_fallback()
        assert not _contains_devanagari(fb["explanation_urdu"])

    def test_fallback_confidence_note_urdu_no_devanagari(self):
        fb = safe_fallback()
        assert not _contains_devanagari(fb["confidence_note_urdu"])

    def test_fallback_conditions_urdu_empty(self):
        fb = safe_fallback()
        assert fb["possible_conditions_urdu"] == []

    def test_fallback_with_reason_no_devanagari(self):
        fb = safe_fallback("some failure reason")
        assert not _contains_devanagari(fb["explanation_urdu"])
        assert not _contains_devanagari(fb["confidence_note_urdu"])


# ---------------------------------------------------------------------------
# 5. Prompt templates — contain required language rules
# ---------------------------------------------------------------------------

class TestPromptLanguageRules:
    def test_system_instruction_says_pakistani_urdu(self):
        assert "Pakistani Urdu" in _SYSTEM_INSTRUCTION

    def test_system_instruction_excludes_devanagari(self):
        assert "Devanagari" in _SYSTEM_INSTRUCTION
        assert "MUST NOT" in _SYSTEM_INSTRUCTION

    def test_base_prompt_urdu_rule_mentions_script(self):
        assert "Urdu/Arabic script" in _BASE_PROMPT

    def test_base_prompt_excludes_devanagari(self):
        assert "Devanagari" in _BASE_PROMPT

    def test_strict_prompt_excludes_devanagari(self):
        assert "Devanagari" in _STRICT_PROMPT

    def test_strict_prompt_says_pakistani_urdu(self):
        assert "Pakistani Urdu" in _STRICT_PROMPT


# ---------------------------------------------------------------------------
# 6. next_steps_service — server-generated Urdu is Devanagari-free
# ---------------------------------------------------------------------------

class TestNextStepsUrdu:
    def test_emergency_urdu_no_devanagari(self):
        for step in _EMERGENCY_STEPS_URDU:
            assert not _contains_devanagari(step)

    def test_medium_urdu_no_devanagari(self):
        for step in _MEDIUM_STEPS_URDU:
            assert not _contains_devanagari(step)

    def test_low_urdu_no_devanagari(self):
        for step in _LOW_STEPS_URDU:
            assert not _contains_devanagari(step)

    @pytest.mark.parametrize("urgency", ["high", "medium", "low"])
    def test_build_safe_next_steps_urdu_no_devanagari(self, urgency):
        result = build_safe_next_steps(urgency_level=urgency, is_red_flag=False)
        for step in result["safe_next_steps_urdu"]:
            assert not _contains_devanagari(step)

    def test_red_flag_escalation_urdu_no_devanagari(self):
        result = build_safe_next_steps(urgency_level="low", is_red_flag=True)
        for step in result["safe_next_steps_urdu"]:
            assert not _contains_devanagari(step)

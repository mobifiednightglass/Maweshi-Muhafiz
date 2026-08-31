"""
Tests for RedFlagService — English and Urdu emergency keyword detection.

Covers:
  1. English emergency symptoms  → is_red_flag: True
  2. Urdu emergency symptoms     → is_red_flag: True
  3. Normal English symptoms     → is_red_flag: False
  4. Normal Urdu symptoms        → is_red_flag: False
  5. All existing English keywords continue to work
  6. Edge cases (empty input, mixed-language text, multiple matches)
"""

import pytest

from app.services.red_flag_service import RedFlagService, RED_FLAG_KEYWORDS


@pytest.fixture
def service():
    return RedFlagService()


# ---------------------------------------------------------------------------
# 1. English emergency symptoms → is_red_flag: True
# ---------------------------------------------------------------------------

class TestEnglishRedFlags:
    """Existing English emergency keywords must all trigger red-flag."""

    @pytest.mark.parametrize("keyword", [
        "difficulty breathing",
        "can't breathe",
        "cant breathe",
        "gasping",
        "unable to stand",
        "can't stand",
        "cant stand",
        "collapsed",
        "heavy bleeding",
        "profuse bleeding",
        "major swelling",
        "severe swelling",
        "convulsions",
        "seizure",
        "unconscious",
    ])
    def test_english_keyword_alone_triggers_red_flag(self, service, keyword):
        result = service.check_red_flags(keyword)
        assert result["is_red_flag"] is True
        assert keyword in result["matched_keywords"]

    def test_english_keyword_in_sentence(self, service):
        result = service.check_red_flags("The goat is gasping and can't stand up")
        assert result["is_red_flag"] is True
        assert "gasping" in result["matched_keywords"]
        assert "can't stand" in result["matched_keywords"]

    def test_case_insensitive_match(self, service):
        result = service.check_red_flags("SEVERE SWELLING on the left leg")
        assert result["is_red_flag"] is True
        assert "severe swelling" in result["matched_keywords"]


# ---------------------------------------------------------------------------
# 2. Urdu emergency symptoms → is_red_flag: True
# ---------------------------------------------------------------------------

class TestUrduRedFlags:
    """Urdu emergency keywords must trigger red-flag just like English ones."""

    @pytest.mark.parametrize("keyword,description", [
        ("سانس لینے میں دشواری", "difficulty breathing"),
        ("سانس لینے میں مشکل", "difficulty breathing (alt.)"),
        ("سانس کے لیے ہانپنا", "gasping for breath"),
        ("سانس نہیں لے سکتا", "can't breathe"),
        ("کھڑا نہیں ہو سکتا", "unable to stand / can't stand"),
        ("گر گیا", "collapsed / fallen"),
        ("بے ہوش", "unconscious"),
        ("زیادہ خون بہنا", "heavy bleeding"),
        ("خون کا بہاؤ", "blood flow / bleeding"),
        ("سخت سوجن", "severe swelling"),
        ("بڑی سوجن", "major swelling"),
        ("دورے", "seizures / convulsions"),
        ("تڑپنا", "convulsions / twitching"),
    ])
    def test_urdu_keyword_alone_triggers_red_flag(self, service, keyword, description):
        result = service.check_red_flags(keyword)
        assert result["is_red_flag"] is True, (
            f"Urdu keyword '{keyword}' ({description}) should trigger red-flag"
        )
        assert keyword in result["matched_keywords"]

    def test_urdu_keyword_in_sentence(self, service):
        result = service.check_red_flags(
            "جانور کو سانس لینے میں دشواری ہو رہی ہے"
        )
        assert result["is_red_flag"] is True
        assert "سانس لینے میں دشواری" in result["matched_keywords"]

    def test_urdu_multiple_keywords_matched(self, service):
        result = service.check_red_flags(
            "جانور بے ہوش ہے اور سخت سوجن ہے"
        )
        assert result["is_red_flag"] is True
        assert "بے ہوش" in result["matched_keywords"]
        assert "سخت سوجن" in result["matched_keywords"]


# ---------------------------------------------------------------------------
# 3. Normal English symptoms → is_red_flag: False
# ---------------------------------------------------------------------------

class TestNormalEnglishSymptoms:
    """Non-emergency English symptoms must NOT trigger red-flag."""

    @pytest.mark.parametrize("symptoms", [
        "The animal is limping slightly on the front left leg",
        "Mild swelling near the knee, animal is eating normally",
        "The cow has been coughing occasionally for two days",
        "Skin looks dry and flaky around the ears",
        "Loss of appetite for the past day",
    ])
    def test_normal_english_symptoms_no_red_flag(self, service, symptoms):
        result = service.check_red_flags(symptoms)
        assert result["is_red_flag"] is False
        assert result["matched_keywords"] == []


# ---------------------------------------------------------------------------
# 4. Normal Urdu symptoms → is_red_flag: False
# ---------------------------------------------------------------------------

class TestNormalUrduSymptoms:
    """Non-emergency Urdu symptoms must NOT trigger red-flag."""

    @pytest.mark.parametrize("symptoms", [
        "جانور ہلکا سا لنگڑا رہا ہے",              # animal is limping slightly
        "کانوں کے پاس جلد خشک ہے",                 # skin is dry near ears
        "ایک دن سے بھوک نہیں لگ رہی",              # no appetite for one day
        "معمولی کھانسی ہو رہی ہے",                  # mild cough
    ])
    def test_normal_urdu_symptoms_no_red_flag(self, service, symptoms):
        result = service.check_red_flags(symptoms)
        assert result["is_red_flag"] is False
        assert result["matched_keywords"] == []


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases: empty input, mixed-language text, etc."""

    def test_empty_string(self, service):
        result = service.check_red_flags("")
        assert result["is_red_flag"] is False
        assert result["matched_keywords"] == []

    def test_none_like_empty(self, service):
        result = service.check_red_flags("")
        assert result["is_red_flag"] is False

    def test_mixed_english_and_urdu_text(self, service):
        """Text containing both English and Urdu with an emergency keyword."""
        result = service.check_red_flags(
            "The animal is gasping and سانس لینے میں دشواری"
        )
        assert result["is_red_flag"] is True
        assert "gasping" in result["matched_keywords"]
        assert "سانس لینے میں دشواری" in result["matched_keywords"]

    def test_mixed_text_no_emergency(self, service):
        """Mixed-language text without any emergency keywords."""
        result = service.check_red_flags(
            "The animal is limping and ہلکا سا لنگڑا رہا ہے"
        )
        assert result["is_red_flag"] is False
        assert result["matched_keywords"] == []


# ---------------------------------------------------------------------------
# 6. Keyword list integrity
# ---------------------------------------------------------------------------

class TestKeywordListIntegrity:
    """Ensure the keyword list contains both English and Urdu entries."""

    def test_english_keywords_present(self):
        assert "difficulty breathing" in RED_FLAG_KEYWORDS
        assert "gasping" in RED_FLAG_KEYWORDS
        assert "unconscious" in RED_FLAG_KEYWORDS

    def test_urdu_keywords_present(self):
        assert "سانس لینے میں دشواری" in RED_FLAG_KEYWORDS
        assert "بے ہوش" in RED_FLAG_KEYWORDS
        assert "سخت سوجن" in RED_FLAG_KEYWORDS

    def test_original_english_keywords_not_removed(self):
        """All 15 original English keywords must still be present."""
        original_english = [
            "difficulty breathing",
            "can't breathe",
            "cant breathe",
            "gasping",
            "unable to stand",
            "can't stand",
            "cant stand",
            "collapsed",
            "heavy bleeding",
            "profuse bleeding",
            "major swelling",
            "severe swelling",
            "convulsions",
            "seizure",
            "unconscious",
        ]
        for kw in original_english:
            assert kw in RED_FLAG_KEYWORDS, f"Missing English keyword: {kw}"

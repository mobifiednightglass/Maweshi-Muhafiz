"""
RedFlagService — keyword-based emergency detection for livestock symptoms.

Performs fast, case-insensitive phrase matching against a curated list of
critical-sign keywords.  This is a lightweight safety net that runs alongside
(or before) the AI vision assessment so the frontend can immediately surface
an emergency banner even if the AI call is slow or fails.

Usage:
    from app.services.red_flag_service import RedFlagService

    service = RedFlagService()
    result  = service.check_red_flags("The goat is gasping and can't stand")
    # result == {"is_red_flag": True, "matched_keywords": ["gasping", "can't stand"]}
"""

# ---------------------------------------------------------------------------
# Red-flag keyword list — extend as needed
# ---------------------------------------------------------------------------
# Each entry is a phrase that signals a potential emergency when found in
# the farmer's symptom description.  Matching is case-insensitive substring.
# Both English and Urdu phrases are supported so farmers can report
# emergencies in either language.
RED_FLAG_KEYWORDS: list[str] = [
    # ── English keywords ──────────────────────────────────────────────
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
    # ── Urdu keywords (اردو) ──────────────────────────────────────────
    # Breathing difficulties
    "سانس لینے میں دشواری",     # difficulty breathing
    "سانس لینے میں مشکل",      # difficulty breathing (alt.)
    "سانس کے لیے ہانپنا",       # gasping for breath
    "سانس نہیں لے سکتا",        # can't breathe
    # Standing / collapse
    "کھڑا نہیں ہو سکتا",        # unable to stand / can't stand
    "گر گیا",                   # collapsed / fallen down
    "بے ہوش",                   # unconscious
    # Bleeding
    "زیادہ خون بہنا",           # heavy bleeding
    "خون کا بہاؤ",             # blood flow / bleeding
    # Swelling
    "سخت سوجن",                 # severe swelling
    "بڑی سوجن",                 # major swelling
    # Seizures / convulsions
    "دورے",                     # seizures / convulsions
    "تڑپنا",                    # convulsions / twitching
]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class RedFlagService:
    """Detects emergency 'red-flag' indicators in free-text symptom input."""

    def __init__(self, keywords: list[str] | None = None):
        # Allow override for testing / future extension; default to the
        # module-level constant.
        self._keywords = keywords if keywords is not None else RED_FLAG_KEYWORDS

    def check_red_flags(self, symptoms_text: str) -> dict:
        """Scan *symptoms_text* for red-flag phrases.

        Parameters
        ----------
        symptoms_text : str
            Free-text symptom description provided by the farmer.

        Returns
        -------
        dict
            ``is_red_flag``       — True when at least one keyword matched.
            ``matched_keywords``  — List of keyword phrases that were found.
        """
        if not symptoms_text:
            return {"is_red_flag": False, "matched_keywords": []}

        text_lower = symptoms_text.lower()
        matched = [kw for kw in self._keywords if kw in text_lower]

        return {
            "is_red_flag": len(matched) > 0,
            "matched_keywords": matched,
        }

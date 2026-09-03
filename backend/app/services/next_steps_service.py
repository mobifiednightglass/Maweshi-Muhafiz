"""
NextStepsService — server-generated, plain-language guidance for farmers.

Builds the ``safe_next_steps`` / ``safe_next_steps_urdu`` fields that are
attached to every health-assessment result.  This guidance is generated on
the server (NOT by the AI) so that:

  * it is always available, even when the AI call fails or falls back, and
  * its wording can be curated for safety — it contains only safe handling
    advice and when to seek professional help, never treatment
    instructions or medication dosages (the AI system prompt forbids the
    model from giving those too).

Guidance is tiered by the assessment's urgency level and escalated to the
emergency tier whenever the red-flag check fired, because a keyword match
or AI-judged high urgency means the case may be time-critical even when
the detailed diagnosis is unavailable.

Usage:
    from app.services.next_steps_service import build_safe_next_steps

    steps = build_safe_next_steps(urgency_level="medium", is_red_flag=False)
    # steps == {"safe_next_steps": [...], "safe_next_steps_urdu": [...]}
"""

# ---------------------------------------------------------------------------
# Tiered guidance — English and Urdu lists must stay parallel (same length,
# same order) so the frontend can render either language interchangeably.
# ---------------------------------------------------------------------------

# ── Emergency tier: red-flag symptoms or AI-judged high urgency ────────────
_EMERGENCY_STEPS: list[str] = [
    "Contact a veterinarian immediately — the reported signs may indicate an emergency.",
    "Keep the animal calm and still in a safe, shaded place; avoid moving it.",
    "Keep the animal separated from other animals if possible.",
    "Do not give any medication or home remedies without a veterinarian's instructions.",
]

_EMERGENCY_STEPS_URDU: list[str] = [
    "فوراً ویٹرنری ڈاکٹر سے رابطہ کریں — جانور کی علامات ہنگامی صورت حال کی نشاندہی کر سکتی ہیں۔",
    "جانور کو پرسکون اور محفوظ، سایہ دار جگہ پر رکھیں اور اسے ہلانا نہیں چاہیے۔",
    "ممکن ہو تو جانور کو دوسرے جانوروں سے الگ رکھیں۔",
    "ویٹرنری ڈاکٹر کے مشورے کے بغیر جانور کو کوئی دوا یا گھریلو علاج نہ دیں۔",
]

# ── Medium tier: AI urgency "medium" (or unknown — safe default) ───────────
_MEDIUM_STEPS: list[str] = [
    "Arrange a veterinary check-up within the next day or two.",
    "Watch the animal closely and note any changes in eating, breathing, or behaviour.",
    "Ensure clean water, shade, and proper feed are available at all times.",
    "If the signs get worse, contact a veterinarian immediately.",
]

_MEDIUM_STEPS_URDU: list[str] = [
    "اگلے ایک یا دو دن میں ویٹرنری ڈاکٹر سے معائنہ کروائیں۔",
    "جانور پر قریب سے نظر رکھیں اور کھانے، سانس یا رویے میں کسی تبدیلی کو نوٹ کریں۔",
    "جانور کو ہر وقت صاف پانی، سایہ اور مناسب خوراک میسر ہو۔",
    "اگر علامات بڑھ جائیں تو فوراً ویٹرنری ڈاکٹر سے رابطہ کریں۔",
]

# ── Low tier: AI urgency "low" — monitor at home ───────────────────────────
_LOW_STEPS: list[str] = [
    "Keep monitoring the animal over the next few days.",
    "Ensure clean water, shade, and proper feed are available.",
    "If the signs continue or worsen, consult a veterinarian.",
]

_LOW_STEPS_URDU: list[str] = [
    "اگلے چند دن تک جانور پر نظر رکھیں۔",
    "صاف پانی، سایہ اور مناسب خوراک دستیاب رکھیں۔",
    "اگر علامات جاری رہیں یا بڑھ جائیں تو ویٹرنری ڈاکٹر سے مشورہ کریں۔",
]

_TIERS: dict[str, tuple[list[str], list[str]]] = {
    "emergency": (_EMERGENCY_STEPS, _EMERGENCY_STEPS_URDU),
    "medium": (_MEDIUM_STEPS, _MEDIUM_STEPS_URDU),
    "low": (_LOW_STEPS, _LOW_STEPS_URDU),
}

# Unknown / missing urgency maps here — "medium" is the safe middle ground.
_DEFAULT_TIER = "medium"


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_safe_next_steps(urgency_level: str | None, is_red_flag: bool) -> dict:
    """Build bilingual safe-next-steps guidance for an assessment.

    Parameters
    ----------
    urgency_level : str | None
        The AI-assessed urgency (``"low"`` | ``"medium"`` | ``"high"``) or
        ``None`` / anything unrecognized (treated as ``"medium"``).
    is_red_flag : bool
        Whether the red-flag keyword check or AI urgency marked this case
        as a potential emergency.  ``True`` always escalates to the
        emergency tier.

    Returns
    -------
    dict
        ``safe_next_steps``       — list of English guidance strings.
        ``safe_next_steps_urdu``  — list of parallel Urdu guidance strings.
    """
    if is_red_flag or urgency_level == "high":
        tier = "emergency"
    elif urgency_level == "low":
        tier = "low"
    else:
        tier = _DEFAULT_TIER

    steps, steps_urdu = _TIERS[tier]
    # Return copies so callers can freely mutate the merged result without
    # corrupting the module-level guidance for later assessments.
    return {
        "safe_next_steps": list(steps),
        "safe_next_steps_urdu": list(steps_urdu),
    }

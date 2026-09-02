"""
InsightService — aggregates health-assessment statistics by animal region.

Reads the data the app already stores (animals + their health assessments)
and groups assessment counts per region: total assessments and flagged /
urgent cases.  Regions come from the optional ``region`` field on the
animal profile; animals without a region fall into the "unknown" bucket.
"""

from app.repositories.base import HealthAssessmentRepository
from app.services.animal_service import AnimalService

# Bucket for animals whose profile has no region set
UNKNOWN_REGION = "unknown"

# diagnosis_result urgency levels that count as urgent, alongside the
# explicit is_red_flag marker (mirrors the assessment flow, where
# is_red_flag = keyword match OR AI urgency "high").
URGENT_URGENCY_LEVELS = {"high"}


class InsightService:
    """Encapsulates read-only insight/aggregation logic."""

    def __init__(
        self,
        animal_service: AnimalService,
        health_assessment_repo: HealthAssessmentRepository,
    ):
        self._animal_service = animal_service
        self._health_assessment_repo = health_assessment_repo

    # ---- Read -----------------------------------------------------------

    def get_regional_insights(self, user_id) -> list[dict]:
        """Return per-region assessment counts for the user's animals.

        Every lookup is scoped to *user_id*: only the user's own animals
        (and therefore their assessments) are counted.  Regions with no
        assessments are omitted.  Results are sorted by total assessments
        (descending), then region name, so ordering is deterministic.
        """
        animals = self._animal_service.get_all(user_id=user_id)

        stats: dict[str, dict] = {}
        for animal in animals:
            region_key = self._region_key(animal)
            assessments = self._health_assessment_repo.get_by_animal_id(
                animal["id"]
            )
            for assessment in assessments:
                entry = stats.setdefault(
                    region_key,
                    {
                        "region": region_key,
                        "total_assessments": 0,
                        "flagged_cases": 0,
                    },
                )
                entry["total_assessments"] += 1
                if self._is_flagged(assessment):
                    entry["flagged_cases"] += 1

        return sorted(
            stats.values(),
            key=lambda entry: (-entry["total_assessments"], entry["region"]),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _region_key(animal: dict) -> str:
        """Return the animal's region, or the "unknown" bucket label."""
        region = animal.get("region")
        if isinstance(region, str) and region.strip():
            return region.strip()
        return UNKNOWN_REGION

    @staticmethod
    def _is_flagged(assessment: dict) -> bool:
        """Return True when an assessment is flagged or urgent."""
        if assessment.get("is_red_flag"):
            return True
        diagnosis = assessment.get("diagnosis_result")
        if isinstance(diagnosis, dict):
            urgency = diagnosis.get("urgency_level")
            return (
                isinstance(urgency, str)
                and urgency.lower() in URGENT_URGENCY_LEVELS
            )
        return False

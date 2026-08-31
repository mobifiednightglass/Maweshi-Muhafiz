"""
HealthAssessmentService — business logic for AI-assisted health assessments.

Receives a ``VisionAssessmentProvider`` via constructor injection so the
underlying AI model (Gemini today, another provider tomorrow) can be
swapped without touching this class.

This service is responsible ONLY for orchestrating the AI vision call.
Persistence (``HealthAssessmentRepository``) and image storage
(``ImageStorageService``) are composed by the route layer, keeping each
component independently testable and replaceable.

Usage:
    from app.services.vision_provider import GeminiVisionProvider
    from app.services.health_assessment_service import HealthAssessmentService


    provider = GeminiVisionProvider(api_key=...)
    service  = HealthAssessmentService(provider)
    result   = service.run_assessment(image_bytes, "image/jpeg", "Limping, swollen leg")
"""
#basic flow of the health assessment service is route, HealthAssessmentService, GeminiVisionProvider, Gemini AI 
import logging

from app.services.vision_provider import VisionAssessmentProvider, safe_fallback
from app.utils.auth_middleware import require_auth
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exceptions — routes catch these and map to HTTP status codes
# ---------------------------------------------------------------------------

class AssessmentError(Exception):
    """Raised when the AI assessment fails in a way that should be surfaced.

    The safe-fallback dict is always available via ``self.fallback`` so the
    caller can still return a meaningful response to the client.
    """

    def __init__(self, message: str, fallback: dict | None = None):
        self.fallback = fallback or safe_fallback(message)
        super().__init__(message)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class HealthAssessmentService:
    """Orchestrates AI-powered vision assessments for livestock health.

    This class is intentionally thin: it delegates to the injected
    ``VisionAssessmentProvider`` and adds a final safety net for any
    exception that might escape the provider's own error handling.
    """

    def __init__(self, provider: VisionAssessmentProvider):
        self._provider = provider

    def run_assessment(
        self,
        image_bytes: bytes,
        image_content_type: str,
        symptoms: str,
    ) -> dict:
        """Run the AI vision assessment and return a structured result dict.

        The returned dict always contains:
        ``possible_conditions`` (list[str]), ``explanation`` (str),
        ``confidence_note`` (str), ``urgency_level`` ("low"|"medium"|"high"),
        ``possible_conditions_urdu`` (list[str]), ``explanation_urdu`` (str),
        ``confidence_note_urdu`` (str).

        If the underlying provider raises any exception, the safe fallback
        dict is returned instead — the caller never sees an unhandled error.

        Parameters
        ----------
        image_bytes : bytes
            Raw image data (already validated and read from the upload).
        image_content_type : str
            MIME type of the image (e.g. ``"image/jpeg"``).
        symptoms : str
            Free-text symptom description provided by the farmer.

        Returns
        -------
        dict
            Structured assessment result.  On any failure, returns
            ``safe_fallback()`` with ``urgency_level = "medium"`` and a
            recommendation for manual vet review.
        """
        try:
            result = self._provider.assess(
                image_bytes=image_bytes,
                image_content_type=image_content_type,
                symptoms=symptoms,
            )
            # Belt-and-suspenders: validate the provider actually returned
            # the expected shape before passing it up.
            if not isinstance(result, dict):
                logger.error(
                    "Provider returned non-dict result (%s); using fallback.",
                    type(result).__name__,
                )
                return safe_fallback("AI provider returned an unexpected response format.")
            return result

        except Exception as exc:
            logger.exception(
                "Unhandled error in HealthAssessmentService.run_assessment: %s",
                exc,
            )
            return safe_fallback(f"Unexpected internal error: {exc}")

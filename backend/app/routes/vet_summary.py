"""
Vet-Ready Case Summary routes — Flask Blueprint registered under /api.

Endpoints
---------
POST   /api/animals/<animal_id>/assessments/<assessment_id>/summary  — create
GET    /api/animals/<animal_id>/assessments/<assessment_id>/summary  — retrieve

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, g, jsonify

from app.services.animal_service import AnimalNotFoundError
from app.utils.auth_middleware import require_auth

vet_summary_bp = Blueprint("vet_summary", __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _success(data=None, message="Operation successful.", status=200):
    body = {"success": True, "message": message, "data": data}
    return jsonify(body), status


def _error(message, error_detail=None, status=400):
    body = {"success": False, "message": message, "error": error_detail or message}
    return jsonify(body), status


# Animal fields to snapshot into the summary
_ANIMAL_SNAPSHOT_FIELDS = (
    "id", "name", "animal_type", "breed", "gender",
    "age", "weight", "color", "health_status",
)


def _verify_animal_and_assessment(animal_id, assessment_id, user_id):
    """Verify the animal belongs to the user and the assessment belongs to
    the animal.

    Returns ``(assessment_record, animal_record, error_response)`` — when
    ``error_response`` is not ``None`` the caller should return it
    immediately.
    """
    # -- 1. Verify animal ownership -----------------------------------------
    try:
        animal = current_app.animal_service.get_by_id(animal_id, user_id)
    except AnimalNotFoundError:
        return None, None, _error(
            f"Animal with id {animal_id} not found.", status=404,
        )
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return None, None, _error("An unexpected error occurred.", status=500)

    # -- 2. Verify assessment exists and belongs to this animal --------------
    try:
        assessment = current_app.health_assessment_repo.get_by_id(assessment_id)
    except Exception:
        logger.exception(
            "Unexpected error fetching assessment %s", assessment_id,
        )
        return None, None, _error("An unexpected error occurred.", status=500)

    if assessment is None:
        return None, None, _error(
            f"Assessment with id {assessment_id} not found.", status=404,
        )

    if str(assessment.get("animal_id")) != str(animal_id):
        return None, None, _error(
            f"Assessment {assessment_id} does not belong to animal {animal_id}.",
            status=404,
        )

    return assessment, animal, None


# ---------------------------------------------------------------------------
# POST /animals/<animal_id>/assessments/<assessment_id>/summary
# ---------------------------------------------------------------------------

@vet_summary_bp.route(
    "/animals/<animal_id>/assessments/<assessment_id>/summary",
    methods=["POST"],
)
@require_auth
def create_summary(animal_id, assessment_id):
    """Create (or return existing) Vet-Ready Case Summary."""

    assessment, animal, err = _verify_animal_and_assessment(
        animal_id, assessment_id, g.user_id,
    )
    if err is not None:
        return err

    # -- 3. Check for existing summary (idempotent) -------------------------
    existing = current_app.vet_summary_repo.get_by_assessment_id(
        assessment_id, g.user_id,
    )
    if existing is not None:
        # Backfill animal snapshot if it was stored before the feature existed
        if not existing.get("animal"):
            animal_snapshot = {
                field: animal.get(field) for field in _ANIMAL_SNAPSHOT_FIELDS
            }
            updated = current_app.vet_summary_repo.update_animal(
                assessment_id, g.user_id, animal_snapshot,
            )
            if updated is not None:
                existing = updated
        return _success(
            data=existing,
            message="Vet case summary already exists.",
            status=200,
        )

    # -- 4. Build animal snapshot ------------------------------------------
    animal_snapshot = {
        field: animal.get(field) for field in _ANIMAL_SNAPSHOT_FIELDS
    }

    # -- 5. Create the summary from the assessment + animal snapshot -------
    try:
        summary = current_app.vet_summary_repo.create({
            "user_id": g.user_id,
            "animal_id": animal_id,
            "assessment_id": assessment_id,
            "symptoms": assessment.get("symptoms"),
            "image_ids": assessment.get("image_ids", []),
            "diagnosis_result": assessment.get("diagnosis_result"),
            "status": assessment.get("status"),
            "is_red_flag": assessment.get("is_red_flag", False),
            "red_flag_reasons": assessment.get("red_flag_reasons", []),
            "animal": animal_snapshot,
        })
    except Exception:
        logger.exception("Unexpected error creating vet summary")
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=summary,
        message="Vet case summary created successfully.",
        status=201,
    )


# ---------------------------------------------------------------------------
# GET /animals/<animal_id>/assessments/<assessment_id>/summary
# ---------------------------------------------------------------------------

@vet_summary_bp.route(
    "/animals/<animal_id>/assessments/<assessment_id>/summary",
    methods=["GET"],
)
@require_auth
def get_summary(animal_id, assessment_id):
    """Retrieve an existing Vet-Ready Case Summary."""

    _, _, err = _verify_animal_and_assessment(
        animal_id, assessment_id, g.user_id,
    )
    if err is not None:
        return err

    summary = current_app.vet_summary_repo.get_by_assessment_id(
        assessment_id, g.user_id,
    )
    if summary is None:
        return _error(
            "Vet case summary not found for this assessment.",
            status=404,
        )

    return _success(
        data=summary,
        message="Vet case summary retrieved successfully.",
    )

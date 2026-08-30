"""
Health-assessment routes — Flask Blueprint registered under /api.

Endpoints
---------
POST   /api/animals/<animal_id>/assessments   — create assessment (multipart)
GET    /api/animals/<animal_id>/assessments   — list assessments for animal
GET    /api/assessments/<assessment_id>       — get single assessment

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, jsonify, request

from app.services.animal_service import AnimalNotFoundError
from app.services.image_storage import ImageValidationError

health_assessments_bp = Blueprint("health_assessments", __name__)
logger = logging.getLogger(__name__)

# Fallback indicator — when the AI provider returns a safe fallback the
# confidence_note always contains this substring.
_FALLBACK_MARKER = "Automated assessment could not be completed"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _success(data=None, message="Operation successful.", status=200):
    body = {"success": True, "message": message, "data": data}
    return jsonify(body), status


def _error(message, error_detail=None, status=400):
    body = {"success": False, "message": message, "error": error_detail or message}
    return jsonify(body), status


# ---------------------------------------------------------------------------
# POST /animals/<animal_id>/assessments
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/animals/<animal_id>/assessments", methods=["POST"],
)
def create_assessment(animal_id):
    """Create a health assessment from an uploaded image + symptoms text.

    Accepts ``multipart/form-data`` with:
      - ``image``   — file field (required)
      - ``symptoms`` — text field (required)
    """

    # -- 1. Verify the animal exists ----------------------------------------
    try:
        current_app.animal_service.get_by_id(animal_id)
    except AnimalNotFoundError:
        return _error(
            f"Animal with id {animal_id} not found.",
            status=404,
        )
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    # -- 2. Extract form fields ---------------------------------------------
    symptoms = request.form.get("symptoms", "").strip()
    if not symptoms:
        return _error("'symptoms' field is required and must not be empty.", status=400)

    image_file = request.files.get("image")
    if image_file is None or image_file.filename == "":
        return _error("'image' file field is required.", status=400)

    # -- 3. Validate symptoms via validate_assessment_data ------------------
    # Animal existence was already verified above, so no animal_repo needed.
    from app.services.health_validation import validate_assessment_data

    validation_payload = {
        "animal_id": animal_id,
        "symptoms": symptoms,
    }
    errors = validate_assessment_data(validation_payload)
    if errors:
        return _error("Validation failed.", error_detail=errors, status=400)

    # -- 4. Check image quality BEFORE saving --------------------------------
    try:
        image_data = image_file.stream.read()
        quality_result = current_app.image_quality_service.check_quality(image_data)

        if not quality_result["is_acceptable"]:
            return _error(
                "Image quality check failed.",
                error_detail=quality_result["issues"],
                status=400,
            )

        # Reset stream position so save_image can read it again
        image_file.stream.seek(0)
    except Exception:
        logger.exception("Unexpected error during image quality check for animal %s", animal_id)
        return _error("An unexpected error occurred while checking image quality.", status=500)

    # -- 5. Save the image via ImageStorageService --------------------------
    try:
        file_id = current_app.image_storage_service.save_image(
            file_stream=image_file.stream,
            filename=image_file.filename,
            content_type=image_file.content_type,
        )
    except ImageValidationError as exc:
        return _error("Image validation failed.", error_detail=exc.errors, status=400)
    except Exception:
        logger.exception("Unexpected error saving image for animal %s", animal_id)
        return _error("An unexpected error occurred while storing the image.", status=500)

    # -- 6. Create a pending HealthAssessment record ------------------------
    try:
        record = current_app.health_assessment_repo.create({
            "animal_id": animal_id,
            "symptoms": symptoms,
            "image_ids": [file_id],
            "status": "pending",
        })
    except Exception:
        logger.exception("Unexpected error creating assessment record")
        return _error("An unexpected error occurred.", status=500)

    # -- 7. Run the AI assessment -------------------------------------------
    try:
        diagnosis_result = current_app.health_assessment_service.run_assessment(
            image_bytes=image_data,
            image_content_type=image_file.content_type,
            symptoms=symptoms,
        )
    except Exception:
        logger.exception("Unexpected error running AI assessment")
        diagnosis_result = None

    # -- 8. Determine final status and update the record --------------------
    if diagnosis_result is None:
        status_value = "failed"
        diagnosis_result = {
            "possible_conditions": [],
            "explanation": "Assessment could not be completed due to an internal error.",
            "confidence_note": "Manual veterinary review is strongly recommended.",
            "urgency_level": "medium",
        }
    elif _FALLBACK_MARKER in diagnosis_result.get("confidence_note", ""):
        status_value = "failed"
    else:
        status_value = "completed"

    try:
        updated = current_app.health_assessment_repo.update(
            record["id"],
            {"diagnosis_result": diagnosis_result, "status": status_value},
        )
        if updated is not None:
            record = updated
        else:
            record["diagnosis_result"] = diagnosis_result
            record["status"] = status_value
    except Exception:
        logger.exception("Unexpected error updating assessment record %s", record["id"])
        record["diagnosis_result"] = diagnosis_result
        record["status"] = status_value

    # Always return 200 — fallback is a valid safe response, not a request error.
    return _success(
        data=record,
        message="Health assessment created successfully.",
        status=200,
    )


# ---------------------------------------------------------------------------
# GET /animals/<animal_id>/assessments
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/animals/<animal_id>/assessments", methods=["GET"],
)
def list_assessments(animal_id):
    """List all health assessments for a given animal."""

    # Verify the animal exists first
    try:
        current_app.animal_service.get_by_id(animal_id)
    except AnimalNotFoundError:
        return _error(
            f"Animal with id {animal_id} not found.",
            status=404,
        )
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    try:
        assessments = current_app.health_assessment_repo.get_by_animal_id(animal_id)
    except Exception:
        logger.exception(
            "Unexpected error listing assessments for animal %s", animal_id,
        )
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=assessments,
        message="Assessments retrieved successfully.",
    )


# ---------------------------------------------------------------------------
# GET /assessments/<assessment_id>
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/assessments/<assessment_id>", methods=["GET"],
)
def get_assessment(assessment_id):
    """Retrieve a single health assessment by its id."""
    try:
        record = current_app.health_assessment_repo.get_by_id(assessment_id)
    except Exception:
        logger.exception("Unexpected error fetching assessment %s", assessment_id)
        return _error("An unexpected error occurred.", status=500)

    if record is None:
        return _error(
            f"Assessment with id {assessment_id} not found.",
            status=404,
        )

    return _success(
        data=record,
        message="Assessment retrieved successfully.",
    )

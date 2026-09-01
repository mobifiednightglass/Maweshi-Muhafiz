"""
Health-assessment routes — Flask Blueprint registered under /api.

Endpoints
---------
POST   /api/animals/<animal_id>/assessments   — create assessment (multipart)
GET    /api/animals/<animal_id>/assessments   — list assessments for animal
GET    /api/assessments/<assessment_id>       — get single assessment (ownership verified)
GET    /api/images/<image_id>                 — get raw image bytes (ownership verified)

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}

Exception: GET /images/<image_id> returns raw binary bytes with the
appropriate Content-Type header instead of the JSON envelope.
"""

import logging

from flask import Blueprint, Response, current_app, g, jsonify, request

from app.services.animal_service import AnimalNotFoundError
from app.services.image_storage import ImageValidationError
from app.utils.auth_middleware import require_auth

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
@require_auth
def create_assessment(animal_id):
    """Create a health assessment from an uploaded image + symptoms text.

    Accepts ``multipart/form-data`` with:
      - ``image``   — file field (required)
      - ``symptoms`` — text field (required)
    """

    # -- 1. Verify the animal exists ----------------------------------------
    try:
        current_app.animal_service.get_by_id(animal_id, g.user_id)
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

    # -- 6. Run red-flag keyword check on symptoms -------------------------
    red_flag_result = current_app.red_flag_service.check_red_flags(symptoms)
    keyword_matched = red_flag_result["is_red_flag"]
    matched_keywords = red_flag_result["matched_keywords"]

    # -- 7. Create a pending HealthAssessment record ------------------------
    try:
        record = current_app.health_assessment_repo.create({
            "animal_id": animal_id,
            "symptoms": symptoms,
            "image_ids": [file_id],
            "status": "pending",
            "is_red_flag": keyword_matched,
            "red_flag_reasons": list(matched_keywords),
        })
    except Exception:
        logger.exception("Unexpected error creating assessment record")
        return _error("An unexpected error occurred.", status=500)

    # -- 8. Run the AI assessment -------------------------------------------
    try:
        diagnosis_result = current_app.health_assessment_service.run_assessment(
            image_bytes=image_data,
            image_content_type=image_file.content_type,
            symptoms=symptoms,
        )
    except Exception:
        logger.exception("Unexpected error running AI assessment")
        diagnosis_result = None

    # -- 9. Determine final status and red-flag state ----------------------
    if diagnosis_result is None:
        status_value = "failed"
        diagnosis_result = {
            "possible_conditions": [],
            "explanation": "Assessment could not be completed due to an internal error.",
            "confidence_note": "Manual veterinary review is strongly recommended.",
            "urgency_level": "medium",
            # Urdu fallback fields
            "possible_conditions_urdu": [],
            "explanation_urdu": (
                "خودکار تشخیص مکمل نہیں ہو سکی۔ "
                "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
            ),
            "confidence_note_urdu": (
                "خودکار تشخیص مکمل نہیں ہو سکی۔ "
                "براہ کرم تجربہ کار ڈاکٹر (ویٹرنری) سے جانور کا معائنہ کروائیں۔"
            ),
        }
    elif _FALLBACK_MARKER in diagnosis_result.get("confidence_note", ""):
        status_value = "failed"
    else:
        status_value = "completed"

    # Combine keyword matches with AI urgency to determine final red-flag state
    ai_urgency_high = diagnosis_result.get("urgency_level") == "high"
    final_is_red_flag = keyword_matched or ai_urgency_high
    print(f"[DEBUG] keyword_matched={keyword_matched}, ai_urgency_high={ai_urgency_high}, urgency_level={diagnosis_result.get('urgency_level')!r}, final={final_is_red_flag}", flush=True)
    red_flag_reasons = list(matched_keywords)
    if ai_urgency_high:
        red_flag_reasons.append("AI assessed urgency as high")

    try:
        updated = current_app.health_assessment_repo.update(
            record["id"],
            {
                "diagnosis_result": diagnosis_result,
                "status": status_value,
                "is_red_flag": final_is_red_flag,
                "red_flag_reasons": red_flag_reasons,
            },
        )
        if updated is not None:
            record = updated
        else:
            record["diagnosis_result"] = diagnosis_result
            record["status"] = status_value
            record["is_red_flag"] = final_is_red_flag
            record["red_flag_reasons"] = red_flag_reasons
    except Exception:
        logger.exception("Unexpected error updating assessment record %s", record["id"])
        record["diagnosis_result"] = diagnosis_result
        record["status"] = status_value
        record["is_red_flag"] = final_is_red_flag
        record["red_flag_reasons"] = red_flag_reasons

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
@require_auth
def list_assessments(animal_id):
    """List all health assessments for a given animal."""

    # Verify the animal exists first
    try:
            current_app.animal_service.get_by_id(animal_id, g.user_id)
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
@require_auth
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

    # -- Ownership verification: the assessment's animal must belong to
    #    the requesting user.  Return 404 (not 403) to hide existence
    #    from non-owners, consistent with the animal ownership pattern.
    try:
        current_app.animal_service.get_by_id(record["animal_id"], g.user_id)
    except AnimalNotFoundError:
        return _error(
            f"Assessment with id {assessment_id} not found.",
            status=404,
        )
    except Exception:
        logger.exception("Unexpected error verifying ownership of assessment %s", assessment_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=record,
        message="Assessment retrieved successfully.",
    )


# ---------------------------------------------------------------------------
# GET /images/<image_id>
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/images/<image_id>", methods=["GET"],
)
@require_auth
def get_image(image_id):
    """Retrieve a stored assessment image by its file id.

    Returns the raw image bytes with the correct Content-Type header
    (NOT wrapped in the JSON envelope).  Access is restricted to the
    user who owns the health assessment that references this image.
    """
    image_storage = getattr(current_app, "image_storage_service", None)
    if image_storage is None:
        return _error("Image retrieval is not available in this environment.", status=503)

    # -- 1. Look up the image in storage -----------------------------------
    try:
        result = image_storage.get_image(image_id)
    except Exception:
        logger.exception("Unexpected error retrieving image %s from storage", image_id)
        return _error("An unexpected error occurred.", status=500)

    if result is None:
        return _error(f"Image with id {image_id} not found.", status=404)

    image_data, content_type = result

    # -- 2. Authorize: find the assessment referencing this image, then
    #    verify the assessment's animal belongs to g.user_id. -------------
    try:
        assessment = current_app.health_assessment_repo.get_by_image_id(image_id)
    except Exception:
        logger.exception("Unexpected error looking up assessment for image %s", image_id)
        return _error("An unexpected error occurred.", status=500)

    if assessment is None:
        return _error(f"Image with id {image_id} not found.", status=404)

    try:
        current_app.animal_service.get_by_id(assessment["animal_id"], g.user_id)
    except AnimalNotFoundError:
        return _error(f"Image with id {image_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error verifying ownership of image %s", image_id)
        return _error("An unexpected error occurred.", status=500)

    # -- 3. Return raw bytes with correct Content-Type ---------------------
    return Response(image_data, mimetype=content_type)

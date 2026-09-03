"""
Health-assessment routes — Flask Blueprint registered under /api.

Endpoints
---------
POST   /api/animals/<animal_id>/assessments   — create assessment (multipart)
POST   /api/animals/<animal_id>/symptoms/voice — create assessment from an
                                                  Urdu voice note (multipart)
GET    /api/animals/<animal_id>/assessments   — list assessments for animal
GET    /api/animals/<animal_id>/assessments/compare — compare two assessments
GET    /api/assessments/<assessment_id>       — get single assessment (ownership verified)
GET    /api/animals/<animal_id>/assessments/<assessment_id>/speech
                                             — Urdu safe-next-steps guidance as
                                               spoken WAV audio (ownership verified)
GET    /api/images/<image_id>                 — get raw image bytes (ownership verified)

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}

Exception: GET /images/<image_id> and GET /assessments/<id>/speech return
raw binary bytes with the appropriate Content-Type header instead of the
JSON envelope.
"""

import logging

from flask import Blueprint, Response, current_app, g, jsonify, request

from app.services.animal_service import AnimalNotFoundError
from app.services.image_storage import ImageValidationError
from app.services.next_steps_service import build_safe_next_steps
from app.services.voice_service import (
    AudioFormatError,
    NoSpeechDetectedError,
    SpeechSynthesisError,
    TranscriptionError,
)
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


def _verify_animal(animal_id):
    """Verify the animal exists and belongs to the current user.

    Returns an error response when verification fails, or ``None`` when the
    caller may proceed.
    """
    try:
        current_app.animal_service.get_by_id(animal_id, g.user_id)
        return None
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)


def _run_assessment_pipeline(animal_id, symptoms, image_file):
    """Run the shared assessment pipeline for the text and voice endpoints.

    Validates the symptoms and image, stores the image, creates a pending
    assessment record, runs the AI assessment, attaches safe-next-steps
    guidance, and persists the final record.

    Returns ``(record, None)`` on success, or ``(None, error_response)``
    when a client error (validation / image quality) prevents the
    assessment from being created.
    """
    # -- 1. Validate symptoms via validate_assessment_data ------------------
    # Animal existence was already verified by the caller.
    from app.services.health_validation import validate_assessment_data

    validation_payload = {
        "animal_id": animal_id,
        "symptoms": symptoms,
    }
    errors = validate_assessment_data(validation_payload)
    if errors:
        return None, _error("Validation failed.", error_detail=errors, status=400)

    # -- 2. Check image quality BEFORE saving --------------------------------
    try:
        image_data = image_file.stream.read()
        quality_result = current_app.image_quality_service.check_quality(image_data)

        if not quality_result["is_acceptable"]:
            return None, _error(
                "Image quality check failed.",
                error_detail=quality_result["issues"],
                status=400,
            )

        # Reset stream position so save_image can read it again
        image_file.stream.seek(0)
    except Exception:
        logger.exception("Unexpected error during image quality check for animal %s", animal_id)
        return None, _error("An unexpected error occurred while checking image quality.", status=500)

    # -- 3. Save the image via ImageStorageService -------------------------
    try:
        file_id = current_app.image_storage_service.save_image(
            file_stream=image_file.stream,
            filename=image_file.filename,
            content_type=image_file.content_type,
        )
    except ImageValidationError as exc:
        return None, _error("Image validation failed.", error_detail=exc.errors, status=400)
    except Exception:
        logger.exception("Unexpected error saving image for animal %s", animal_id)
        return None, _error("An unexpected error occurred while storing the image.", status=500)

    # -- 4. Run red-flag keyword check on symptoms -------------------------
    red_flag_result = current_app.red_flag_service.check_red_flags(symptoms)
    keyword_matched = red_flag_result["is_red_flag"]
    matched_keywords = red_flag_result["matched_keywords"]

    # -- 5. Create a pending HealthAssessment record ------------------------
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
        return None, _error("An unexpected error occurred.", status=500)

    # -- 6. Run the AI assessment -------------------------------------------
    try:
        diagnosis_result = current_app.health_assessment_service.run_assessment(
            image_bytes=image_data,
            image_content_type=image_file.content_type,
            symptoms=symptoms,
        )
    except Exception:
        logger.exception("Unexpected error running AI assessment")
        diagnosis_result = None

    # -- 7. Blur rejection (merged into the single Gemini call) -----------
    # If the AI flagged the image as too blurry, clean up and reject.
    if isinstance(diagnosis_result, dict) and diagnosis_result.get("image_too_blurry"):
        # Delete the pending assessment record
        try:
            current_app.health_assessment_repo.delete(record["id"])
        except Exception:
            logger.exception("Failed to delete pending assessment record %s after blur rejection", record["id"])
        # Delete the saved image
        try:
            current_app.image_storage_service.delete_image(file_id)
        except Exception:
            logger.exception("Failed to delete image %s after blur rejection", file_id)
        return None, _error(
            "Image is too blurry to analyze. Please upload a clearer photo.",
            status=400,
        )

    # -- 8. Animal-presence rejection (same single Gemini call) -----------
    # If the AI determined the photo does not contain an animal, clean up and reject.
    if isinstance(diagnosis_result, dict) and diagnosis_result.get("contains_animal") is False:
        try:
            current_app.health_assessment_repo.delete(record["id"])
        except Exception:
            logger.exception("Failed to delete pending assessment record %s after animal-presence rejection", record["id"])
        try:
            current_app.image_storage_service.delete_image(file_id)
        except Exception:
            logger.exception("Failed to delete image %s after animal-presence rejection", file_id)
        return None, _error(
            "No animal was detected in this photo. Please upload a clear photo of the animal.",
            status=400,
        )

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
    red_flag_reasons = list(matched_keywords)
    if ai_urgency_high:
        red_flag_reasons.append("AI assessed urgency as high")

    # -- 8. Attach server-generated safe-next-steps guidance ----------------
    # Generated on the server (not by the AI) so the farmer always receives
    # safe handling advice, even when the AI assessment failed or fell back.
    diagnosis_result.update(
        build_safe_next_steps(
            urgency_level=diagnosis_result.get("urgency_level"),
            is_red_flag=final_is_red_flag,
        )
    )

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

    return record, None


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
    error = _verify_animal(animal_id)
    if error:
        return error

    # -- 2. Extract form fields ---------------------------------------------
    symptoms = request.form.get("symptoms", "").strip()
    if not symptoms:
        return _error("'symptoms' field is required and must not be empty.", status=400)

    image_file = request.files.get("image")
    if image_file is None or image_file.filename == "":
        return _error("'image' file field is required.", status=400)

    # -- 3. Run the shared assessment pipeline -------------------------------
    record, pipeline_error = _run_assessment_pipeline(animal_id, symptoms, image_file)
    if pipeline_error:
        return pipeline_error

    # Always return 200 — fallback is a valid safe response, not a request error.
    return _success(
        data=record,
        message="Health assessment created successfully.",
        status=200,
    )


# ---------------------------------------------------------------------------
# POST /animals/<animal_id>/symptoms/voice
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/animals/<animal_id>/symptoms/voice", methods=["POST"],
)
@require_auth
def create_voice_assessment(animal_id):
    """Create a health assessment from an Urdu voice note + photo.

    Accepts ``multipart/form-data`` with:
      - ``audio`` — file field (required): the farmer describing the
        animal's symptoms in Urdu (e.g. a WhatsApp voice note).
      - ``image`` — file field (required): a photo of the animal.

    The audio is transcribed to Urdu text, which feeds into the same
    assessment pipeline as typed symptoms.  The response includes both the
    transcript and the full assessment record.
    """

    # -- 1. Verify the animal exists ----------------------------------------
    error = _verify_animal(animal_id)
    if error:
        return error

    # -- 2. Extract file fields ----------------------------------------------
    audio_file = request.files.get("audio")
    if audio_file is None or audio_file.filename == "":
        return _error("'audio' file field is required.", status=400)

    image_file = request.files.get("image")
    if image_file is None or image_file.filename == "":
        return _error("'image' file field is required.", status=400)

    # -- 3. Transcribe the Urdu voice note into symptom text ------------------
    try:
        audio_bytes = audio_file.stream.read()
        transcribed_symptoms = current_app.voice_service.transcribe_urdu_audio(
            audio_bytes=audio_bytes,
            filename=audio_file.filename,
            content_type=audio_file.content_type,
        )
    except NoSpeechDetectedError:
        return _error(
            "No understandable speech was detected in the audio. "
            "Please try recording the symptoms again.",
            status=400,
        )
    except AudioFormatError as exc:
        return _error("Unsupported audio format.", error_detail=str(exc), status=400)
    except TranscriptionError as exc:
        logger.exception("Speech transcription failed for animal %s", animal_id)
        return _error(
            "Speech transcription is currently unavailable. "
            "Please try again shortly.",
            error_detail=str(exc),
            status=502,
        )

    # -- 4. Feed the transcript into the shared assessment pipeline ------------
    record, pipeline_error = _run_assessment_pipeline(
        animal_id, transcribed_symptoms, image_file,
    )
    if pipeline_error:
        return pipeline_error

    return _success(
        data={
            "transcribed_symptoms": transcribed_symptoms,
            "assessment": record,
        },
        message="Voice symptoms transcribed and assessed successfully.",
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
    error = _verify_animal(animal_id)
    if error:
        return error

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
# GET /animals/<animal_id>/assessments/compare
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/animals/<animal_id>/assessments/compare",
    methods=["GET"],
)
@require_auth
def compare_assessments(animal_id):
    """Return two assessments of one animal side by side.

    Query parameters:
      - ``assessment_id_1`` — id of the first (e.g. "before") assessment
      - ``assessment_id_2`` — id of the second (e.g. "after") assessment
    """

    # -- 1. Verify the animal exists and belongs to the user ----------------
    error = _verify_animal(animal_id)
    if error:
        return error

    # -- 2. Extract required query parameters -------------------------------
    id_1 = request.args.get("assessment_id_1", "").strip()
    id_2 = request.args.get("assessment_id_2", "").strip()
    if not id_1 or not id_2:
        return _error(
            "Both 'assessment_id_1' and 'assessment_id_2' query "
            "parameters are required.",
            status=400,
        )

    # -- 3. Fetch both assessments ------------------------------------------
    try:
        assessment_1 = current_app.health_assessment_repo.get_by_id(id_1)
        assessment_2 = current_app.health_assessment_repo.get_by_id(id_2)
    except Exception:
        logger.exception(
            "Unexpected error fetching assessments %s and %s", id_1, id_2,
        )
        return _error("An unexpected error occurred.", status=500)

    # -- 4. Both must exist and belong to the animal in the URL -------------
    # 404 (not 403) for missing/mismatched assessments hides existence from
    # non-owners, consistent with the rest of this module.
    for record, assessment_id in ((assessment_1, id_1), (assessment_2, id_2)):
        if record is None or str(record.get("animal_id")) != str(animal_id):
            return _error(
                f"Assessment with id {assessment_id} not found.",
                status=404,
            )

    return _success(
        data={"assessment_1": assessment_1, "assessment_2": assessment_2},
        message="Assessment comparison retrieved successfully.",
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
# GET /animals/<animal_id>/assessments/<assessment_id>/speech
# ---------------------------------------------------------------------------

@health_assessments_bp.route(
    "/animals/<animal_id>/assessments/<assessment_id>/speech",
    methods=["GET"],
)
@require_auth
def get_assessment_speech(animal_id, assessment_id):
    """Return the assessment's Urdu safe-next-steps guidance as spoken audio.

    Reads ``safe_next_steps_urdu`` from the assessment's diagnosis result,
    synthesizes it into Urdu speech via the voice service, and returns the
    WAV audio bytes with an ``audio/wav`` Content-Type — NOT wrapped in the
    JSON envelope (same exception as GET /images/<image_id>).
    """

    # -- 1. Verify the animal exists and belongs to the user ----------------
    error = _verify_animal(animal_id)
    if error:
        return error

    # -- 2. Fetch the assessment ---------------------------------------------
    try:
        record = current_app.health_assessment_repo.get_by_id(assessment_id)
    except Exception:
        logger.exception("Unexpected error fetching assessment %s", assessment_id)
        return _error("An unexpected error occurred.", status=500)

    # 404 (not 403) for missing/mismatched assessments hides existence from
    # non-owners, consistent with the rest of this module.
    if record is None or str(record.get("animal_id")) != str(animal_id):
        return _error(
            f"Assessment with id {assessment_id} not found.",
            status=404,
        )

    # -- 3. Extract the Urdu guidance ----------------------------------------
    diagnosis = record.get("diagnosis_result") or {}
    steps_urdu = [
        step.strip()
        for step in (diagnosis.get("safe_next_steps_urdu") or [])
        if isinstance(step, str) and step.strip()
    ]
    if not steps_urdu:
        return _error(
            "Speech guidance is not available for this assessment.",
            status=404,
        )

    # -- 4. Synthesize the Urdu speech ---------------------------------------
    try:
        wav_bytes = current_app.voice_service.urdu_text_to_speech(
            "\n".join(steps_urdu)
        )
    except SpeechSynthesisError as exc:
        logger.exception("Speech synthesis failed for assessment %s", assessment_id)
        return _error(
            "Speech synthesis is currently unavailable. "
            "Please try again shortly.",
            error_detail=str(exc),
            status=502,
        )

    # -- 5. Return raw WAV bytes with the correct Content-Type ---------------
    return Response(wav_bytes, mimetype="audio/wav")


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

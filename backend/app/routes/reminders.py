"""
Animal health reminder routes — Flask Blueprint registered under /api.

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, g, jsonify, request

from app.services.animal_service import AnimalNotFoundError
from app.services.reminder_service import (
    ReminderNotFoundError,
    ValidationError,
)
from app.utils.auth_middleware import require_auth

reminders_bp = Blueprint("reminders", __name__)
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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@reminders_bp.route("/animals/<animal_id>/reminders", methods=["POST"])
@require_auth
def create_reminder(animal_id):
    # -- 1. Verify the animal exists and belongs to the user ----------------
    try:
        current_app.animal_service.get_by_id(animal_id, g.user_id)
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    # -- 2. Validate and persist the reminder -------------------------------
    data = request.get_json(silent=True)
    if data is None:
        return _error("Request body must be valid JSON.", status=400)

    try:
        reminder = current_app.reminder_service.create(
            data, animal_id=animal_id, user_id=g.user_id
        )
    except ValidationError as exc:
        return _error("Validation failed.", error_detail=exc.errors, status=400)
    except Exception:
        logger.exception("Unexpected error creating reminder for animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(data=reminder, message="Reminder created successfully.", status=201)


@reminders_bp.route("/animals/<animal_id>/reminders", methods=["GET"])
@require_auth
def list_reminders(animal_id):
    # -- 1. Verify the animal exists and belongs to the user ----------------
    try:
        current_app.animal_service.get_by_id(animal_id, g.user_id)
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error verifying animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    # -- 2. Fetch the reminders ---------------------------------------------
    try:
        reminders = current_app.reminder_service.get_by_animal_id(
            animal_id, g.user_id
        )
    except Exception:
        logger.exception("Unexpected error listing reminders for animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(data=reminders, message="Reminders retrieved successfully.")


@reminders_bp.route("/reminders/<reminder_id>", methods=["DELETE"])
@require_auth
def delete_reminder(reminder_id):
    try:
        current_app.reminder_service.get_by_id(reminder_id, g.user_id)
        current_app.reminder_service.delete(reminder_id, g.user_id)
    except ReminderNotFoundError:
        return _error(f"Reminder with id {reminder_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error deleting reminder %s", reminder_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(message="Reminder deleted successfully.")

"""
Animal health passport routes — Flask Blueprint registered under /api.

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, g, jsonify

from app.services.animal_service import AnimalNotFoundError
from app.utils.auth_middleware import require_auth

passport_bp = Blueprint("passport", __name__)
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

@passport_bp.route("/animals/<animal_id>/passport", methods=["GET"])
@require_auth
def get_animal_passport(animal_id):
    try:
        passport = current_app.passport_service.get_passport(
            animal_id, user_id=g.user_id
        )
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error building passport for animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(data=passport, message="Animal passport retrieved successfully.")

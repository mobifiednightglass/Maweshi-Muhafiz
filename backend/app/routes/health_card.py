"""
Animal health card routes — Flask Blueprint registered under /api.

The health card is a simplified, buyer-facing view of an animal's health.
All responses follow the consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, g, jsonify

from app.services.animal_service import AnimalNotFoundError
from app.utils.auth_middleware import require_auth

health_card_bp = Blueprint("health_card", __name__)
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

@health_card_bp.route("/animals/<animal_id>/health-card", methods=["GET"])
@require_auth
def get_animal_health_card(animal_id):
    try:
        health_card = current_app.health_card_service.get_health_card(
            animal_id, user_id=g.user_id
        )
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error building health card for animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=health_card,
        message="Animal health card retrieved successfully.",
    )

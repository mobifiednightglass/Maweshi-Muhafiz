"""
Animal CRUD routes — Flask Blueprint registered under /api.

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, jsonify, request

from app.services.animal_service import AnimalNotFoundError, ValidationError

animals_bp = Blueprint("animals", __name__)
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

@animals_bp.route("/animals", methods=["POST"])
def create_animal():
    data = request.get_json(silent=True)
    if data is None:
        return _error("Request body must be valid JSON.", status=400)

    try:
        from flask import current_app
        animal = current_app.animal_service.create(data)
    except ValidationError as exc:
        return _error("Validation failed.", error_detail=exc.errors, status=400)
    except Exception:
        logger.exception("Unexpected error creating animal")
        return _error("An unexpected error occurred.", status=500)

    return _success(data=animal, message="Animal created successfully.", status=201)


@animals_bp.route("/animals", methods=["GET"])
def list_animals():
    try:
        from flask import current_app
        animals = current_app.animal_service.get_all()
    except Exception:
        logger.exception("Unexpected error listing animals")
        return _error("An unexpected error occurred.", status=500)

    return _success(data=animals, message="Animals retrieved successfully.")


@animals_bp.route("/animals/<animal_id>", methods=["GET"])
def get_animal(animal_id):
    try:
        from flask import current_app
        animal = current_app.animal_service.get_by_id(animal_id)
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error fetching animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(data=animal, message="Animal retrieved successfully.")


@animals_bp.route("/animals/<animal_id>", methods=["PUT"])
def update_animal(animal_id):
    data = request.get_json(silent=True)
    if data is None:
        return _error("Request body must be valid JSON.", status=400)

    try:
        from flask import current_app
        animal = current_app.animal_service.update(animal_id, data)
    except ValidationError as exc:
        return _error("Validation failed.", error_detail=exc.errors, status=400)
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error updating animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(data=animal, message="Animal updated successfully.")


@animals_bp.route("/animals/<animal_id>", methods=["DELETE"])
def delete_animal(animal_id):
    try:
        from flask import current_app
        current_app.animal_service.delete(animal_id)
    except AnimalNotFoundError:
        return _error(f"Animal with id {animal_id} not found.", status=404)
    except Exception:
        logger.exception("Unexpected error deleting animal %s", animal_id)
        return _error("An unexpected error occurred.", status=500)

    return _success(message="Animal deleted successfully.")

"""
Authentication routes — Flask Blueprint registered under /api.

Provides signup and login endpoints with JWT token generation.

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, jsonify, request

from app.services.auth_service import (
    AuthenticationError,
    DuplicateEmailError,
    ValidationError,
)

auth_bp = Blueprint("auth", __name__)
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

@auth_bp.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)
    if data is None:
        return _error("Request body must be valid JSON.", status=400)

    try:
        from flask import current_app
        result = current_app.auth_service.signup(data)
    except ValidationError as exc:
        return _error("Validation failed.", error_detail=exc.errors, status=400)
    except DuplicateEmailError as exc:
        return _error(str(exc), status=409)
    except Exception:
        logger.exception("Unexpected error during signup")
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=result,
        message="User registered successfully.",
        status=201,
    )


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if data is None:
        return _error("Request body must be valid JSON.", status=400)

    try:
        from flask import current_app
        result = current_app.auth_service.login(data)
    except ValidationError as exc:
        return _error("Validation failed.", error_detail=exc.errors, status=400)
    except AuthenticationError:
        return _error("Invalid email or password.", status=401)
    except Exception:
        logger.exception("Unexpected error during login")
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=result,
        message="Login successful.",
    )

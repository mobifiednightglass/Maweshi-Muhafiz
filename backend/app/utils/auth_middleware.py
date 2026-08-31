"""
JWT authentication middleware — verifies tokens on protected routes.
"""

from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def _error(message, status):
    return jsonify({
        "success": False,
        "message": message,
        "error": message,
    }), status


def require_auth(f):
    """Decorator that requires a valid JWT in the Authorization header.

    On success, attaches g.user_id and g.user_email.
    On failure, returns a 401 JSON error and does NOT call the route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return _error("Missing or malformed Authorization header.", 401)

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return _error("Missing or malformed Authorization header.", 401)

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return _error("Token has expired.", 401)
        except jwt.InvalidTokenError:
            return _error("Invalid token.", 401)

        g.user_id = payload.get("user_id")
        g.user_email = payload.get("email")

        if g.user_id is None:
            return _error("Invalid token payload.", 401)

        return f(*args, **kwargs)

    return decorated
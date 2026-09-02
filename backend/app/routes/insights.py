"""
Insight routes — Flask Blueprint registered under /api.

Endpoints
---------
GET /api/insights/area — health-assessment counts grouped by animal region

All responses follow a consistent envelope:
    Success → {"success": true,  "message": "...", "data": ...}
    Error   → {"success": false, "message": "...", "error":  "..."}
"""

import logging

from flask import Blueprint, current_app, g, jsonify

from app.utils.auth_middleware import require_auth

insights_bp = Blueprint("insights", __name__)
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

@insights_bp.route("/insights/area", methods=["GET"])
@require_auth
def get_area_insights():
    try:
        insights = current_app.insight_service.get_regional_insights(
            user_id=g.user_id
        )
    except Exception:
        logger.exception("Unexpected error building regional insights")
        return _error("An unexpected error occurred.", status=500)

    return _success(
        data=insights,
        message="Regional insights retrieved successfully.",
    )

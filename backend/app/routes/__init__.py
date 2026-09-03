from app.routes.health import health_bp
from app.routes.animals import animals_bp
from app.routes.auth import auth_bp
from app.routes.health_assessments import health_assessments_bp
from app.routes.vet_summary import vet_summary_bp
from app.routes.reminders import reminders_bp
from app.routes.passport import passport_bp
from app.routes.insights import insights_bp

__all__ = [
    "health_bp",
    "animals_bp",
    "auth_bp",
    "health_assessments_bp",
    "vet_summary_bp",
    "reminders_bp",
    "passport_bp",
    "insights_bp",
]

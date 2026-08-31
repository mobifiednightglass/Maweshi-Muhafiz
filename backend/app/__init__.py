from flask import Flask
from app.config import get_config


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    _register_blueprints(app)
    _wire_dependencies(app)

    return app


def _register_blueprints(app):
    from app.routes.health import health_bp
    from app.routes.animals import animals_bp
    from app.routes.auth import auth_bp
    from app.routes.health_assessments import health_assessments_bp
    from app.routes.vet_summary import vet_summary_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(animals_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(health_assessments_bp, url_prefix="/api")
    app.register_blueprint(vet_summary_bp, url_prefix="/api")


def _wire_dependencies(app):
    """
    Compose the dependency graph and attach it to the Flask app.

    * "testing"  → InMemory repositories  (fast, no live DB needed)
    * everything else → MongoDB repositories (reads MONGODB_URI from env)

    To swap the repository later, change the conditional below —
    no route or service changes are required.
    """
    from app.services.animal_service import AnimalService
    from app.services.auth_service import AuthService

    if app.config.get("TESTING"):
        from app.repositories.in_memory import InMemoryAnimalRepository
        from app.repositories.in_memory_user import InMemoryUserRepository

        animal_repo = InMemoryAnimalRepository()
        user_repo = InMemoryUserRepository()
    else:
        from app.repositories.mongo import MongoAnimalRepository
        from app.repositories.mongo_user import MongoUserRepository

        uri = app.config["MONGODB_URI"]
        db_name = app.config["MONGODB_DB_NAME"]

        animal_repo = MongoAnimalRepository(uri=uri, db_name=db_name)
        user_repo = MongoUserRepository(uri=uri, db_name=db_name)

    app.animal_service = AnimalService(animal_repo)
    app.auth_service = AuthService(user_repo, app.config["SECRET_KEY"])
    app.user_repo = user_repo

    # -- Health-assessment dependencies ------------------------------------
    from app.services.image_storage import ImageStorageService
    from app.services.health_assessment_service import HealthAssessmentService
    from app.services.image_quality import ImageQualityService
    from app.services.red_flag_service import RedFlagService

    if app.config.get("TESTING"):
        from app.repositories.in_memory_health import InMemoryHealthAssessmentRepository
        from app.repositories.in_memory_vet_summary import InMemoryVetCaseSummaryRepository
        health_assessment_repo = InMemoryHealthAssessmentRepository()
        vet_summary_repo = InMemoryVetCaseSummaryRepository()

        # Testing: use a stub provider that returns safe_fallback immediately
        from app.services.vision_provider import safe_fallback

        class _StubVisionProvider:
            def assess(self, image_bytes, image_content_type, symptoms):
                return safe_fallback("Stub provider — testing mode.")

        vision_provider = _StubVisionProvider()
        image_storage_service = None  # not needed in tests (image save is skipped)
    else:
        from app.repositories.mongo_health import MongoHealthAssessmentRepository
        from app.repositories.mongo_vet_summary import MongoVetCaseSummaryRepository
        from app.services.vision_provider import GeminiVisionProvider

        uri = app.config["MONGODB_URI"]
        db_name = app.config["MONGODB_DB_NAME"]

        health_assessment_repo = MongoHealthAssessmentRepository(uri=uri, db_name=db_name)
        vet_summary_repo = MongoVetCaseSummaryRepository(uri=uri, db_name=db_name)
        vision_provider = GeminiVisionProvider(api_key=app.config["GEMINI_API_KEY"])
        image_storage_service = ImageStorageService(uri=uri, db_name=db_name)

    app.health_assessment_repo = health_assessment_repo
    app.vet_summary_repo = vet_summary_repo
    app.health_assessment_service = HealthAssessmentService(vision_provider)
    app.image_storage_service = image_storage_service
    app.image_quality_service = ImageQualityService()
    app.red_flag_service = RedFlagService()

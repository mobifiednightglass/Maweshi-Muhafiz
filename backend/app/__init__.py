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

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(animals_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")


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

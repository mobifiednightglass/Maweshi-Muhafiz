import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = False
    TESTING = False

    # MongoDB Atlas
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "maweshi_muhafiz")

    # External API keys
    QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    pass


_configs = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    name = name or os.environ.get("FLASK_ENV", "development")
    return _configs.get(name, DevelopmentConfig)


def require_mongodb_uri(config) -> None:
    """Raise a clear startup error when MONGODB_URI is missing or blank.

    Called during app creation in non-testing modes; testing mode uses
    in-memory repositories and never needs the URI.  Without this check,
    MongoClient("") fails with an opaque pymongo ConfigurationError.
    """
    uri = (config.get("MONGODB_URI") or "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not set — check your .env file.")

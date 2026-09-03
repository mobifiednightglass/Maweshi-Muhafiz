"""Tests for the MongoDB configuration guard in app/config.py.

Non-testing modes must fail fast with a clear message when MONGODB_URI
is missing or blank; testing mode (in-memory repositories) must keep
booting without it.
"""

import pytest

from app import create_app
from app.config import DevelopmentConfig, TestingConfig, require_mongodb_uri


class TestRequireMongoDbUri:
    def test_valid_uri_passes(self):
        require_mongodb_uri({"MONGODB_URI": "mongodb://localhost:27017"})

    def test_missing_key_raises(self):
        with pytest.raises(RuntimeError, match="MONGODB_URI is not set"):
            require_mongodb_uri({})

    def test_empty_uri_raises(self):
        with pytest.raises(RuntimeError, match="check your .env"):
            require_mongodb_uri({"MONGODB_URI": ""})

    def test_whitespace_uri_raises(self):
        with pytest.raises(RuntimeError, match="check your .env"):
            require_mongodb_uri({"MONGODB_URI": "   "})

    def test_none_uri_raises(self):
        with pytest.raises(RuntimeError, match="MONGODB_URI is not set"):
            require_mongodb_uri({"MONGODB_URI": None})


class TestStartupGuard:
    def test_development_with_empty_uri_raises_clear_error(self, monkeypatch):
        monkeypatch.setattr(DevelopmentConfig, "MONGODB_URI", "")
        with pytest.raises(
            RuntimeError, match="MONGODB_URI is not set — check your .env file",
        ):
            create_app("development")

    def test_development_with_whitespace_uri_raises(self, monkeypatch):
        monkeypatch.setattr(DevelopmentConfig, "MONGODB_URI", "  ")
        with pytest.raises(RuntimeError, match="MONGODB_URI is not set"):
            create_app("development")

    def test_testing_mode_boots_without_uri(self, monkeypatch):
        monkeypatch.setattr(TestingConfig, "MONGODB_URI", "")
        app = create_app("testing")
        assert app.config["TESTING"] is True
        assert app.config["MONGODB_URI"] == ""

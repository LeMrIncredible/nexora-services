"""
Configuration classes for the Nexora application.

Values can be overridden by environment variables.  A `.env` file (not
committed to source control) may be used during local development.
"""

import os


class Config:
    """Base configuration with sensible defaults."""

    # Generate a random secret key for session security if none provided
    SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME")

    # Database location. Use SQLite by default but allow override via DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.abspath('nexora.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # APScheduler configuration. The API is enabled so jobs can be inspected if needed.
    SCHEDULER_API_ENABLED = True

    # Default mail sender (used by stub email utility). Real email integration can
    # override these values with an SMTP configuration.
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@nexora.local")


class TestConfig(Config):
    """Configuration suitable for testing."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# DEV ONLY: disable CSRF if needed for local troubleshooting
WTF_CSRF_ENABLED = True

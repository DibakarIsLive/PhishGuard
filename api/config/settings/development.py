"""Local development settings for PhishGuard."""

from .base import *  # noqa: F403,F401

DEBUG = False

# Development can accept local hostnames even when .env has not been created.
ALLOWED_HOSTS = sorted(  # noqa: F405
    set([*ALLOWED_HOSTS, "127.0.0.1", "localhost", "testserver"])
)

# Keep browser access convenient during local React/Vite development.
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = sorted(  # noqa: F405
    set(
        [
            *CORS_ALLOWED_ORIGINS,  # noqa: F405
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )
)

# Development logs are useful in the terminal and in api/logs/django.log.
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")  # noqa: F405

# The URL analyzer is network-free, but MongoDB is a required local service for
# normal API startup. manage.py provides an explicit --force bypass for local
# diagnostics when persistence is intentionally unavailable.

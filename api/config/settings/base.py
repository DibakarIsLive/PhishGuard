"""Shared Django settings for every PhishGuard environment."""

from pathlib import Path
import os

from dotenv import load_dotenv


# api/ is the project root for Django.
BASE_DIR = Path(__file__).resolve().parents[2]

# Load api/.env when present. Environment variables already exported by the
# shell take precedence over values loaded from the file.
load_dotenv(BASE_DIR / ".env", override=False)


# -----------------------------------------------------------------------------
# Environment helpers
# -----------------------------------------------------------------------------

def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


# -----------------------------------------------------------------------------
# Core project settings
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "phishguard-development-only-key")
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# -----------------------------------------------------------------------------
# Applications
# -----------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
]

LOCAL_APPS = [
    "web_api",
    "url_analysis",
]

INSTALLED_APPS = [*DJANGO_APPS, *THIRD_PARTY_APPS, *LOCAL_APPS]


# -----------------------------------------------------------------------------
# Middleware and request handling
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

TEMPLATES = []


# -----------------------------------------------------------------------------
# Database boundaries
# -----------------------------------------------------------------------------
# Django's relational ORM is intentionally disabled. Scan history is stored by
# MongoEngine through url_analysis.database, keeping Django from creating SQLite files.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "phishguard")
MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(
    os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "1000")
)
MONGODB_CONNECT_TIMEOUT_MS = int(
    os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "1000")
)
MONGODB_SOCKET_TIMEOUT_MS = int(
    os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "1000")
)
MONGODB_RETRY_INTERVAL_SECONDS = int(
    os.getenv("MONGODB_RETRY_INTERVAL_SECONDS", "30")
)


# -----------------------------------------------------------------------------
# Internationalization and defaults
# -----------------------------------------------------------------------------
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Calcutta")
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -----------------------------------------------------------------------------
# Static files
# -----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# -----------------------------------------------------------------------------
# Cross-origin API access
# -----------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", False)


# -----------------------------------------------------------------------------
# Django REST Framework
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # Authentication is not part of Phase 1; avoid importing django.contrib.auth
    # while the API intentionally uses Django's dummy relational database.
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("API_ANON_RATE", "60/min"),
    },
}


# -----------------------------------------------------------------------------
# Machine-learning paths and API limits
# -----------------------------------------------------------------------------
ML_MODELS_DIR = BASE_DIR / "ml-models"
MODEL_PATH = ML_MODELS_DIR / "phishguard_model.joblib"
MAX_URL_LENGTH = int(os.getenv("MAX_URL_LENGTH", "2048"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "25"))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))

if MAX_URL_LENGTH < 1:
    raise ValueError("MAX_URL_LENGTH must be a positive integer")
if MAX_BATCH_SIZE < 1:
    raise ValueError("MAX_BATCH_SIZE must be a positive integer")
if HISTORY_LIMIT < 1:
    raise ValueError("HISTORY_LIMIT must be a positive integer")


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
}

"""Production settings for PhishGuard deployments."""

from .base import *  # noqa: F403,F401


DEBUG = False

# Production must provide an explicit secret and host list.
if SECRET_KEY == "phishguard-development-only-key":  # noqa: F405
    raise RuntimeError("SECRET_KEY must be set when DJANGO_ENV=production")

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")  # noqa: F405
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must contain at least one host in production")

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")  # noqa: F405
if not CORS_ALLOWED_ORIGINS:
    raise RuntimeError("CORS_ALLOWED_ORIGINS must contain at least one origin in production")

# HTTPS and browser hardening. Set behind a TLS-terminating reverse proxy when
# deploying the API publicly.
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# Allow the reverse proxy to serve collected assets from this directory.
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

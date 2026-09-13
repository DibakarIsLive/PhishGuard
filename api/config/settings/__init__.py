"""Select the Django settings profile from DJANGO_ENV."""

import os


ENVIRONMENT = os.getenv("DJANGO_ENV", "development").strip().lower()

if ENVIRONMENT == "production":
    from .production import *  # noqa: F403,F401
else:
    from .development import *  # noqa: F403,F401

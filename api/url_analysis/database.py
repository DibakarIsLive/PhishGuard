import logging
import time

from django.conf import settings
from mongoengine import connect
from pymongo import MongoClient

logger = logging.getLogger(__name__)
_connected = False
_unavailable_until = 0.0


def mongodb_is_reachable():
    """Return whether MongoDB answers a bounded connectivity probe."""
    client = None
    try:
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
            socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
        )
        client.admin.command("ping")
        return True
    except Exception as exc:
        logger.debug("MongoDB startup preflight failed: %s", exc)
        return False
    finally:
        if client is not None:
            client.close()


def connect_database():
    global _connected, _unavailable_until

    if _connected:
        return True

    now = time.monotonic()
    if now < _unavailable_until:
        return False

    try:
        connect(
            host=settings.MONGODB_URI,
            db=settings.MONGODB_DATABASE,
            alias="default",
            connect=False,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
            socketTimeoutMS=settings.MONGODB_SOCKET_TIMEOUT_MS,
        )
        _connected = True
        return True
    except Exception as exc:
        _unavailable_until = now + settings.MONGODB_RETRY_INTERVAL_SECONDS
        logger.warning("MongoDB unavailable; continuing without persistence: %s", exc)
        return False

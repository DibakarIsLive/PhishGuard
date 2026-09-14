"""Bounded MongoDB connectivity and MongoEngine setup."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import time
from typing import Any

from django.conf import settings
from mongoengine import connect
from pymongo import MongoClient


logger = logging.getLogger(__name__)
_connected = False
_connection_key: tuple[str, str] | None = None
_unavailable_until = 0.0
_last_probe_at: datetime | None = None
_last_probe_ok: bool | None = None


def _record_probe(result: bool) -> bool:
    global _last_probe_at, _last_probe_ok
    _last_probe_at = datetime.now(timezone.utc)
    _last_probe_ok = result
    return result


def mongodb_is_reachable() -> bool:
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
        return _record_probe(True)
    except Exception as exc:
        logger.debug("MongoDB connectivity probe failed: %s", exc)
        return _record_probe(False)
    finally:
        if client is not None:
            client.close()


def database_status(probe: bool = False) -> dict[str, Any]:
    """Return safe, structured database diagnostics without exposing secrets."""
    reachable = mongodb_is_reachable() if probe else _last_probe_ok
    if reachable is True:
        status = "available"
    elif reachable is False:
        status = "unavailable"
    else:
        status = "unknown"

    return {
        "status": status,
        "required_for_normal_startup": True,
        "database": settings.MONGODB_DATABASE,
        "last_checked_at": _last_probe_at.isoformat() if _last_probe_at else None,
    }


def connect_database() -> bool:
    """Configure MongoEngine once, suppressing repeated unavailable retries."""
    global _connected, _connection_key, _unavailable_until

    current_key = (settings.MONGODB_URI, settings.MONGODB_DATABASE)
    if _connected and _connection_key == current_key:
        return True

    now = time.monotonic()
    if now < _unavailable_until:
        return False

    # A bounded probe prevents a forced diagnostic scan from creating a slow
    # MongoEngine save attempt when the database is clearly unavailable.
    if not mongodb_is_reachable():
        _unavailable_until = now + settings.MONGODB_RETRY_INTERVAL_SECONDS
        logger.warning(
            "MongoDB unavailable; continuing without persistence for this retry window."
        )
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
        _connection_key = current_key
        _unavailable_until = 0.0
        return True
    except Exception as exc:
        _unavailable_until = now + settings.MONGODB_RETRY_INTERVAL_SECONDS
        logger.warning("MongoDB connection setup failed; persistence disabled: %s", exc)
        return False


def reset_database_state() -> None:
    """Reset in-process connection diagnostics for tests and local tooling."""
    global _connected, _connection_key, _unavailable_until, _last_probe_at, _last_probe_ok
    _connected = False
    _connection_key = None
    _unavailable_until = 0.0
    _last_probe_at = None
    _last_probe_ok = None

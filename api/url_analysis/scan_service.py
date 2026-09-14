"""Application service for local URL analysis and optional persistence."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlsplit

from django.conf import settings

from .brand_confusion import BRAND_RULES_VERSION, detect_brand_confusion
from .database import connect_database
from .feature_extractor import FEATURE_VERSION, extract_features
from .models import Scan
from .predictor import predict
from .url_validation import URLValidationError, normalize_url


logger = logging.getLogger(__name__)
ANALYZER_VERSION = f"phase1-heuristic/{FEATURE_VERSION}"


def _persist_scan(result: dict[str, Any]) -> None:
    if not connect_database():
        logger.info("Scan analyzed without persistence because MongoDB is unavailable.")
        return

    try:
        document = Scan(
            url=result["url"],
            verdict=result["verdict"],
            confidence=result["confidence"],
            features=result["features"],
            explanations=result["explanations"],
            analyzer_version=ANALYZER_VERSION,
        ).save()
        result["id"] = str(document.id)
        result["created_at"] = document.created_at.isoformat()
    except Exception:
        logger.exception("MongoDB persistence failed after URL analysis.")


def analyze_url(url: str) -> dict[str, Any]:
    """Analyze one URL locally and attempt a best-effort history save."""
    normalized = normalize_url(url, max_length=settings.MAX_URL_LENGTH)
    # urlsplit is intentionally used only to verify a usable network location;
    # it never resolves the hostname or contacts the destination.
    parsed = urlsplit(
        normalized if "://" in normalized else f"http://{normalized}"
    )
    if not parsed.netloc or not parsed.hostname:
        raise URLValidationError("Enter a valid URL with a domain name.")

    features = extract_features(normalized)
    brand_confusion = detect_brand_confusion(normalized)
    verdict, confidence, reasons = predict(features, url=normalized)
    result: dict[str, Any] = {
        "url": normalized,
        "verdict": verdict,
        "confidence": confidence,
        "features": features,
        "explanations": {
            "reasons": reasons,
            "analyzer_version": ANALYZER_VERSION,
            "network_accessed": False,
            "brand_rules_version": BRAND_RULES_VERSION,
            "brand_confusion": brand_confusion,
        },
    }
    _persist_scan(result)
    return result


def recent_scans(limit: int | None = None) -> list[dict[str, Any]]:
    """Return recent persisted summaries, or an empty list if unavailable."""
    requested_limit = settings.HISTORY_LIMIT if limit is None else limit
    bounded_limit = max(1, min(int(requested_limit), settings.HISTORY_LIMIT))
    if not connect_database():
        return []

    try:
        return [
            {
                "id": str(item.id),
                "url": item.url,
                "verdict": item.verdict,
                "confidence": item.confidence,
                "created_at": item.created_at.isoformat(),
            }
            for item in Scan.objects.limit(bounded_limit)
        ]
    except Exception:
        logger.exception("MongoDB history read failed.")
        return []

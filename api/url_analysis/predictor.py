"""Phase 1 prediction boundary: compatible optional model or heuristics."""

from __future__ import annotations

from pathlib import Path
import logging
from typing import Any

import joblib

from django.conf import settings

from .brand_confusion import detect_brand_confusion
from .feature_extractor import FEATURE_NAMES, FEATURE_VERSION


logger = logging.getLogger(__name__)
MODEL_PATH = Path(settings.MODEL_PATH)


def model_status() -> dict[str, Any]:
    """Describe optional model availability without loading untrusted artifacts."""
    if not MODEL_PATH.exists():
        return {
            "status": "fallback",
            "available": False,
            "path": str(MODEL_PATH),
            "feature_version": FEATURE_VERSION,
            "feature_count": len(FEATURE_NAMES),
            "reason": "No optional model artifact is present.",
        }

    return {
        "status": "candidate",
        "available": True,
        "path": str(MODEL_PATH),
        "feature_version": FEATURE_VERSION,
        "feature_count": len(FEATURE_NAMES),
        "reason": "Artifact presence detected; compatibility is checked before inference.",
    }


def _feature_row(features: dict[str, Any]) -> list[list[float | int]]:
    missing = [name for name in FEATURE_NAMES if name not in features]
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing)}")
    return [[features[name] for name in FEATURE_NAMES]]


def _validate_model(model: Any) -> None:
    if not hasattr(model, "predict"):
        raise TypeError("model does not expose predict()")

    model_feature_names = getattr(model, "feature_names_in_", None)
    if model_feature_names is not None:
        observed = tuple(str(name) for name in model_feature_names)
        if observed != FEATURE_NAMES:
            raise ValueError("model feature_names_in_ does not match FEATURE_NAMES")

    n_features = getattr(model, "n_features_in_", None)
    if n_features is not None and int(n_features) != len(FEATURE_NAMES):
        raise ValueError("model feature count does not match FEATURE_NAMES")


def _model_prediction(features: dict[str, Any]) -> tuple[int, float] | None:
    if not MODEL_PATH.exists():
        return None

    try:
        values = _feature_row(features)
        model = joblib.load(MODEL_PATH)
        _validate_model(model)
        prediction = model.predict(values)
        if len(prediction) != 1:
            raise ValueError("model returned an unexpected prediction shape")

        label = int(prediction[0])
        if label not in {0, 1}:
            raise ValueError("model returned a label other than 0 or 1")

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(values)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 0.75

        if not 0 <= confidence <= 1:
            raise ValueError("model confidence is outside the [0, 1] range")
        return label, confidence
    except Exception as exc:
        logger.warning("Optional model is incompatible or unavailable; using heuristics: %s", exc)
        return None


def _heuristic_prediction(
    features: dict[str, Any],
    *,
    brand_confusion: dict[str, Any] | None = None,
) -> tuple[str, float, list[str]]:
    score = 0
    reasons: list[str] = []
    rules = [
        (
            features["has_ip_address"],
            4,
            "The hostname is an IPv4 address",
        ),
        (
            features["has_suspicious_tld"],
            3,
            "The top-level domain is commonly abused",
        ),
        (
            features["has_login_keyword"],
            2,
            "The URL contains an account or login keyword",
        ),
        (
            features["at_count"] > 0,
            3,
            "The @ symbol can hide the actual destination",
        ),
        (
            features["has_punycode"],
            3,
            "The hostname uses punycode",
        ),
        (
            features["has_encoded_character"],
            1,
            "The URL contains encoded characters",
        ),
        (
            features["url_length"] > 100,
            2,
            "The URL is unusually long",
        ),
        (
            features["subdomain_count"] > 2,
            1,
            "The URL contains several subdomains",
        ),
        (
            brand_confusion is not None,
            4,
            brand_confusion["reason"] if brand_confusion else "",
        ),
    ]

    for condition, weight, reason in rules:
        if condition:
            score += weight
            reasons.append(reason)

    if score >= 7:
        return "phishing", round(min(0.98, 0.62 + score / 40), 4), reasons
    if score >= 3:
        return "suspicious", round(min(0.89, 0.55 + score / 30), 4), reasons
    return (
        "legitimate",
        round(max(0.55, 0.92 - score / 20), 4),
        reasons or ["No strong phishing indicators were found"],
    )


def predict(
    features: dict[str, Any],
    *,
    url: str | None = None,
) -> tuple[str, float, list[str]]:
    """Return verdict, bounded confidence, and human-readable reasons.

    ``url`` is optional to preserve the predictor's feature-only contract for
    callers and optional model artifacts. When supplied, the local brand rules
    add an advisory heuristic signal without changing the 20-feature vector.
    """
    brand_confusion = detect_brand_confusion(url) if url else None
    model_result = _model_prediction(features)
    if model_result is not None:
        label, confidence = model_result
        reasons = ["Optional trained model prediction"]
        if brand_confusion is not None:
            reasons.insert(0, brand_confusion["reason"])
        return (
            "phishing" if label else "legitimate",
            round(confidence, 4),
            reasons,
        )

    return _heuristic_prediction(features, brand_confusion=brand_confusion)

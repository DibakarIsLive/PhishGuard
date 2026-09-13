from pathlib import Path
import logging
import joblib
from .feature_extractor import FEATURE_NAMES

logger = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parent.parent / "ml-models" / "phishguard_model.joblib"


def _model_prediction(features):
    if not MODEL_PATH.exists():
        return None
    try:
        model = joblib.load(MODEL_PATH)
        values = [[features[name] for name in FEATURE_NAMES]]
        label = int(model.predict(values)[0])
        probability = float(max(model.predict_proba(values)[0])) if hasattr(model, "predict_proba") else 0.75
        return label, probability
    except Exception as exc:
        logger.exception("Unable to load optional model: %s", exc)
        return None


def predict(features):
    model_result = _model_prediction(features)
    if model_result:
        label, confidence = model_result
        return ("phishing" if label else "legitimate"), round(confidence, 4), ["Optional trained model prediction"]
    score = 0
    reasons = []
    rules = [(features["has_ip_address"], 4, "The hostname is an IP address"), (features["has_suspicious_tld"], 3, "The top-level domain is commonly abused"), (features["has_login_keyword"], 2, "The URL contains an account or login keyword"), (features["at_count"] > 0, 3, "The @ symbol can hide the actual destination"), (features["has_punycode"], 3, "The hostname uses punycode"), (features["has_encoded_character"], 1, "The URL contains encoded characters"), (features["url_length"] > 100, 2, "The URL is unusually long"), (features["subdomain_count"] > 2, 1, "The URL contains several subdomains")]
    for condition, weight, reason in rules:
        if condition:
            score += weight
            reasons.append(reason)
    if score >= 7:
        return "phishing", round(min(0.98, 0.62 + score / 40), 4), reasons
    if score >= 3:
        return "suspicious", round(min(0.89, 0.55 + score / 30), 4), reasons
    return "legitimate", round(max(0.55, 0.92 - score / 20), 4), reasons or ["No strong phishing indicators were found"]

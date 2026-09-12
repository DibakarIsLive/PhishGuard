"""Prediction service: uses a trained model when available, otherwise transparent heuristic scoring."""
from pathlib import Path
import joblib
from .feature_extractor import extract_features

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml_models" / "ensemble.joblib"

RULES = [
    ("has_ip_address", 28, "The address uses a raw IP address instead of a normal domain."),
    ("has_at_symbol", 24, "An @ symbol can hide the true destination domain."),
    ("has_punycode", 22, "Punycode in a domain can be used for look-alike website names."),
    ("has_shortener", 18, "A URL shortener conceals the final destination."),
    ("suspicious_tld", 12, "The top-level domain is frequently abused in phishing campaigns."),
    ("suspicious_keyword_count", 6, "The address contains login, verification, or account-related wording."),
    ("double_slash_in_path", 8, "An extra // inside the path can be used to confuse readers."),
]


def _heuristic(features: dict) -> tuple[float, list]:
    score, explanations = 0.0, []
    for key, weight, text in RULES:
        value = features[key]
        if value:
            contribution = min(weight * value, 30)
            score += contribution
            explanations.append({"feature": key.replace("_", " ").title(), "impact": round(contribution, 1), "reason": text})
    if features["url_length"] > 100:
        score += 10
        explanations.append({"feature": "Long URL", "impact": 10, "reason": "Very long addresses can be used to obscure the destination."})
    if features["hyphen_count"] >= 3:
        score += 8
        explanations.append({"feature": "Many Hyphens", "impact": 8, "reason": "Multiple hyphens are common in impersonating domain names."})
    if features["url_entropy"] > 4.4:
        score += 7
        explanations.append({"feature": "High URL Entropy", "impact": 7, "reason": "The address contains an unusually random pattern of characters."})
    return min(round(score, 1), 100.0), sorted(explanations, key=lambda item: item["impact"], reverse=True)


def predict(url: str) -> dict:
    features = extract_features(url)
    score, explanations = _heuristic(features)
    model_used = "explainable heuristic baseline"
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            columns = model.feature_names_in_.tolist()
            probability = float(model.predict_proba([[features.get(name, 0) for name in columns]])[0][1])
            score = round(probability * 100, 1)
            model_used = "trained ensemble model"
        except Exception:
            pass
    verdict = "phishing" if score >= 50 else "legitimate"
    confidence = round((50 + abs(score - 50)) / 100, 3)
    category = "credential harvesting" if verdict == "phishing" and features["suspicious_keyword_count"] else ("suspicious URL pattern" if verdict == "phishing" else "no strong phishing indicators")
    if not explanations:
        explanations = [{"feature": "No critical red flags", "impact": 0, "reason": "This check found no strong structural phishing indicators. Always verify the website independently before entering sensitive data."}]
    return {"url": url, "verdict": verdict, "confidence": confidence, "risk_score": score, "category": category, "features": features, "explanations": explanations[:5], "model_used": model_used}

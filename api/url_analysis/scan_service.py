from urllib.parse import urlparse
from .database import connect_database
from .feature_extractor import extract_features
from .models import Scan
from .predictor import predict


def analyze_url(url):
    url = url.strip()
    parsed = urlparse(url if "://" in url else f"http://{url}")
    if not parsed.netloc:
        raise ValueError("Enter a valid URL with a domain name.")
    features = extract_features(url)
    verdict, confidence, reasons = predict(features)
    result = {"url": url, "verdict": verdict, "confidence": confidence, "features": features, "explanations": {"reasons": reasons}}
    if connect_database():
        try:
            document = Scan(**result).save()
            result["id"] = str(document.id)
            result["created_at"] = document.created_at.isoformat()
        except Exception:
            pass
    return result


def recent_scans(limit=20):
    if not connect_database():
        return []
    try:
        return [{"id": str(item.id), "url": item.url, "verdict": item.verdict, "confidence": item.confidence, "created_at": item.created_at.isoformat()} for item in Scan.objects.limit(limit)]
    except Exception:
        return []

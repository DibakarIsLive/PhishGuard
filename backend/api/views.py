from django.db.models import Avg, Count
from pathlib import Path
import json
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Prediction
from .serializers import BatchCheckSerializer, URLCheckSerializer
from vision.predictor import predict


def _save(result):
    record = Prediction.objects.create(url=result["url"], verdict=result["verdict"], confidence=result["confidence"], risk_score=result["risk_score"], category=result["category"], features=result["features"], explanations=result["explanations"])
    result["id"] = record.id
    result["checked_at"] = record.created_at
    return result


@api_view(["GET"])
def health(request):
    return Response({"success": True, "data": {"status": "healthy", "service": "PhishGuard API", "time": now()}})


@api_view(["POST"])
def check_url(request):
    serializer = URLCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({"success": True, "data": _save(predict(serializer.validated_data["url"]))}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def batch_check(request):
    serializer = BatchCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    results, errors = [], []
    for index, raw_url in enumerate(serializer.validated_data["urls"]):
        item = URLCheckSerializer(data={"url": raw_url})
        if item.is_valid(): results.append(_save(predict(item.validated_data["url"])))
        else: errors.append({"index": index, "url": raw_url, "errors": item.errors})
    return Response({"success": True, "data": {"results": results, "errors": errors}})


@api_view(["GET"])
def predictions(request):
    try:
        requested_limit = int(request.query_params.get("limit", 20))
    except (TypeError, ValueError):
        requested_limit = 20
    limit = max(1, min(requested_limit, 100))
    records = Prediction.objects.all()[:limit]
    return Response({"success": True, "data": [{"id": item.id, "url": item.url, "verdict": item.verdict, "confidence": item.confidence, "risk_score": item.risk_score, "category": item.category, "checked_at": item.created_at} for item in records]})


@api_view(["GET"])
def stats(request):
    records = Prediction.objects.all()
    total = records.count()
    model_dir = Path(__file__).resolve().parents[1] / "ml_models"
    model_path = model_dir / "ensemble.joblib"
    metadata_path = model_dir / "training_metadata.json"
    training = None
    if metadata_path.exists():
        try:
            training = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            training = None
    return Response({"success": True, "data": {
        "total_checks": total,
        "phishing_detected": records.filter(verdict="phishing").count(),
        "legitimate_detected": records.filter(verdict="legitimate").count(),
        "average_risk_score": round(records.aggregate(value=Avg("risk_score"))["value"] or 0, 1),
        "model_status": "trained ensemble model" if model_path.exists() else "training required",
        "training": training,
    }})

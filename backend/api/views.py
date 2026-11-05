from django.db.models import Avg, Count
from django.db import transaction
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Prediction
import csv
import threading
from pathlib import Path
from io import TextIOWrapper
from .serializers import BatchCheckSerializer, CSVUploadSerializer, URLCheckSerializer
from .models import ScanJob
from vision.predictor import predict


def _save(result, scan_job=None):
    record = Prediction.objects.create(scan_job=scan_job, url=result["url"], verdict=result["verdict"], confidence=result["confidence"], risk_score=result["risk_score"], category=result["category"], features=result["features"], explanations=result["explanations"])
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


def _run_bulk_scan(job_id, csv_path):
    """Development background worker: scans every row while the API remains responsive."""
    try:
        job = ScanJob.objects.get(pk=job_id)
        job.status = "running"
        job.save(update_fields=["status"])
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            url_column = next((name for name in (reader.fieldnames or []) if name.strip().lower() in {"url", "urls", "link", "website"}), None)
            if not url_column:
                raise ValueError("CSV must contain a URL column.")
            rows = list(reader)
        ScanJob.objects.filter(pk=job_id).update(total_rows=len(rows))
        phishing = legitimate = invalid = 0
        for index, row in enumerate(rows, start=1):
            item = URLCheckSerializer(data={"url": row.get(url_column, "")})
            if item.is_valid():
                result = predict(item.validated_data["url"])
                _save(result, job)
                if result["verdict"] == "phishing": phishing += 1
                else: legitimate += 1
            else:
                invalid += 1
            if index % 25 == 0:
                ScanJob.objects.filter(pk=job_id).update(processed_rows=index, phishing_count=phishing, legitimate_count=legitimate, invalid_count=invalid)
        from django.utils.timezone import now
        ScanJob.objects.filter(pk=job_id).update(status="completed", processed_rows=len(rows), phishing_count=phishing, legitimate_count=legitimate, invalid_count=invalid, completed_at=now())
    except Exception as error:
        ScanJob.objects.filter(pk=job_id).update(status="failed", error_message=str(error))


@api_view(["POST"])
def upload_csv(request):
    """Start a background job that scans every URL in the uploaded CSV."""
    serializer = CSVUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    uploaded = serializer.validated_data["file"]
    job = ScanJob.objects.create(source_filename=uploaded.name)
    upload_dir = Path(__file__).resolve().parent.parent / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    csv_path = upload_dir / f"job_{job.id}.csv"
    with open(csv_path, "wb") as destination:
        for chunk in uploaded.chunks(): destination.write(chunk)
    transaction.on_commit(lambda: threading.Thread(target=_run_bulk_scan, args=(job.id, csv_path), daemon=True).start())
    return Response({"success": True, "data": {"job_id": job.id, "status": job.status, "total_rows": 0, "processed_rows": 0, "phishing_count": 0, "legitimate_count": 0, "invalid_count": 0, "faulty_urls": [], "message": "Bulk scan started for every URL in this CSV."}}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def bulk_job_status(request, job_id):
    try:
        job = ScanJob.objects.get(pk=job_id)
    except ScanJob.DoesNotExist:
        return Response({"success": False, "error": "Scan job not found."}, status=404)
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = min(max(int(request.query_params.get("page_size", 50)), 1), 100)
    records = job.predictions.filter(verdict="phishing").order_by("-risk_score")[(page - 1) * page_size:page * page_size]
    faulty_urls = [{"id": item.id, "url": item.url, "risk_score": item.risk_score, "category": item.category, "explanations": item.explanations} for item in records]
    return Response({"success": True, "data": {"job_id": job.id, "source_filename": job.source_filename, "status": job.status, "total_rows": job.total_rows, "processed_rows": job.processed_rows, "phishing_count": job.phishing_count, "legitimate_count": job.legitimate_count, "invalid_count": job.invalid_count, "error": job.error_message, "faulty_urls": faulty_urls, "page": page}})


@api_view(["GET"])
def predictions(request):
    limit = min(int(request.query_params.get("limit", 20)), 100)
    records = Prediction.objects.all()[:limit]
    return Response({"success": True, "data": [{"id": item.id, "url": item.url, "verdict": item.verdict, "confidence": item.confidence, "risk_score": item.risk_score, "category": item.category, "checked_at": item.created_at} for item in records]})


@api_view(["GET"])
def stats(request):
    records = Prediction.objects.all()
    total = records.count()
    return Response({"success": True, "data": {"total_checks": total, "phishing_detected": records.filter(verdict="phishing").count(), "legitimate_detected": records.filter(verdict="legitimate").count(), "average_risk_score": round(records.aggregate(value=Avg("risk_score"))["value"] or 0, 1), "model_status": "baseline ready — add a trained model to backend/ml_models/ensemble.joblib"}})

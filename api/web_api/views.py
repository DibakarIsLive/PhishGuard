"""Django REST views for the Phase 1 API surface."""

from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from url_analysis.brand_confusion import BRAND_RULES_VERSION
from url_analysis.database import database_status
from url_analysis.predictor import model_status
from url_analysis.scan_service import analyze_url, recent_scans
from url_analysis.url_validation import URLValidationError

from .serializers import ScanSerializer


class ApiRootView(APIView):
    def get(self, request):
        return Response(
            {
                "service": "phishguard-api",
                "status": "ok",
                "phase": "phase-1",
                "message": "The PhishGuard API is running.",
                "frontend": "http://127.0.0.1:5173/",
                "endpoints": {
                    "health": "/api/health/",
                    "scan": "/api/scan/",
                    "history": "/api/history/",
                    "capabilities": "/api/capabilities/",
                },
            }
        )


class HealthView(APIView):
    def get(self, request):
        database = database_status(probe=False)
        model = model_status()
        return Response(
            {
                "status": "ok",
                "service": "phishguard-api",
                "phase": "phase-1",
                "analysis": {
                    "status": "available",
                    "network_accessed": False,
                    "brand_confusion_rules": BRAND_RULES_VERSION,
                },
                "database": database,
                "model": model,
            }
        )


class CapabilitiesView(APIView):
    def get(self, request):
        return Response(
            {
                "service": "phishguard-api",
                "phase": "phase-1",
                "analysis": {
                    "single_url": True,
                    "network_accessed": False,
                    "feature_count": 20,
                    "brand_confusion_rules": BRAND_RULES_VERSION,
                },
                "persistence": {
                    "provider": "MongoDB via MongoEngine",
                    "history": True,
                    "best_effort_after_startup": True,
                },
                "model": model_status(),
                "limits": {
                    "max_url_length": settings.MAX_URL_LENGTH,
                    "history_limit": settings.HISTORY_LIMIT,
                },
                "not_available": [
                    "batch scanning",
                    "authentication",
                    "live reputation lookup",
                    "HTML or browser inspection",
                    "SHAP attribution",
                ],
            }
        )


class ScanView(APIView):
    def post(self, request):
        serializer = ScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            return Response(
                analyze_url(serializer.validated_data["url"]),
                status=status.HTTP_200_OK,
            )
        except URLValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class HistoryView(APIView):
    def get(self, request):
        return Response(
            {
                "results": recent_scans(),
                "limit": settings.HISTORY_LIMIT,
            }
        )

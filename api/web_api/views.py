from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ScanSerializer
from url_analysis.scan_service import analyze_url, recent_scans


class ApiRootView(APIView):
    def get(self, request):
        return Response(
            {
                "service": "phishguard-api",
                "status": "ok",
                "message": "The PhishGuard API is running.",
                "frontend": "http://127.0.0.1:5173/",
                "endpoints": {
                    "health": "/api/health/",
                    "scan": "/api/scan/",
                    "history": "/api/history/",
                },
            }
        )


class HealthView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "phishguard-api",
                "database": "MongoDB required for normal startup",
            }
        )


class ScanView(APIView):
    def post(self, request):
        serializer = ScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            return Response(analyze_url(serializer.validated_data["url"]), status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class HistoryView(APIView):
    def get(self, request):
        return Response({"results": recent_scans()})

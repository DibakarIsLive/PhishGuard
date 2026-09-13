from django.urls import path
from .views import HealthView, HistoryView, ScanView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("scan/", ScanView.as_view(), name="scan"),
    path("history/", HistoryView.as_view(), name="history"),
]

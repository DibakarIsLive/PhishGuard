from django.urls import path

from .views import CapabilitiesView, HealthView, HistoryView, ScanView


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("capabilities/", CapabilitiesView.as_view(), name="capabilities"),
    path("scan/", ScanView.as_view(), name="scan"),
    path("history/", HistoryView.as_view(), name="history"),
]

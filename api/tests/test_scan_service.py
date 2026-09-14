from unittest.mock import patch

from django.test import Client, override_settings

from manage import _prepare_runserver_arguments
from url_analysis.scan_service import analyze_url, recent_scans
from url_analysis.url_validation import URLValidationError


def test_api_root_returns_service_details():
    response = Client().get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "phishguard-api"
    assert response.json()["phase"] == "phase-1"
    assert response.json()["endpoints"]["health"] == "/api/health/"


def test_analysis_returns_verdict_and_network_free_metadata():
    result = analyze_url("https://example.com")

    assert result["verdict"] in {"legitimate", "suspicious", "phishing"}
    assert 0 <= result["confidence"] <= 1
    assert result["explanations"]["network_accessed"] is False
    assert result["explanations"]["brand_confusion"] is None


def test_runserver_force_flag_is_removed_before_django_parsing():
    argv, force = _prepare_runserver_arguments(
        ["manage.py", "runserver", "--force", "127.0.0.1:8000"]
    )

    assert argv == ["manage.py", "runserver", "127.0.0.1:8000"]
    assert force is True


def test_non_runserver_commands_are_not_changed():
    argv, force = _prepare_runserver_arguments(["manage.py", "check"])

    assert argv == ["manage.py", "check"]
    assert force is False


def test_health_reports_structured_analysis_database_and_model_state():
    response = Client().get("/api/health/")
    payload = response.json()

    assert response.status_code == 200
    assert payload["analysis"]["network_accessed"] is False
    assert payload["analysis"]["brand_confusion_rules"] == "local-brand-rules-v1"
    assert payload["database"]["required_for_normal_startup"] is True
    assert payload["model"]["feature_count"] == 20


def test_capabilities_report_phase_one_boundaries():
    response = Client().get("/api/capabilities/")
    payload = response.json()

    assert response.status_code == 200
    assert payload["analysis"]["single_url"] is True
    assert "batch scanning" in payload["not_available"]
    assert payload["limits"]["max_url_length"] > 0
    assert payload["analysis"]["brand_confusion_rules"] == "local-brand-rules-v1"


def test_scan_serializer_rejects_internal_whitespace():
    response = Client().post(
        "/api/scan/",
        data={"url": "https://example.com/a b"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "url" in response.json()


def test_scan_serializer_uses_configured_url_limit():
    with override_settings(MAX_URL_LENGTH=12):
        response = Client().post(
            "/api/scan/",
            data={"url": "https://example.com"},
            content_type="application/json",
        )

    assert response.status_code == 400


def test_service_rejects_unsupported_scheme():
    with patch("url_analysis.scan_service._persist_scan"):
        try:
            analyze_url("ftp://example.com/file")
        except URLValidationError as exc:
            assert "HTTP and HTTPS" in str(exc)
        else:
            raise AssertionError("Expected unsupported scheme to be rejected")


def test_history_uses_configured_limit():
    with patch("url_analysis.scan_service.connect_database", return_value=False):
        with override_settings(HISTORY_LIMIT=7):
            assert recent_scans() == []


def test_persistence_failure_does_not_discard_analysis_result():
    with patch("url_analysis.scan_service.connect_database", return_value=True), patch(
        "url_analysis.scan_service.Scan", side_effect=RuntimeError("database down")
    ):
        result = analyze_url("https://example.com")

    assert result["verdict"] in {"legitimate", "suspicious", "phishing"}
    assert "id" not in result
    assert result["explanations"]["brand_rules_version"] == "local-brand-rules-v1"

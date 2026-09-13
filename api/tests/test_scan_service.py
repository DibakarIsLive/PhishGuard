from django.test import Client

from manage import _prepare_runserver_arguments
from url_analysis.scan_service import analyze_url


def test_api_root_returns_service_details():
    response = Client().get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "phishguard-api"
    assert response.json()["endpoints"]["health"] == "/api/health/"


def test_analysis_returns_verdict():
    result = analyze_url("https://example.com")
    assert result["verdict"] in {"legitimate", "suspicious", "phishing"}
    assert 0 <= result["confidence"] <= 1


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


def test_health_reports_mongodb_startup_requirement():
    response = Client().get("/api/health/")

    assert response.status_code == 200
    assert response.json()["database"] == "MongoDB required for normal startup"

from django.test import Client

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

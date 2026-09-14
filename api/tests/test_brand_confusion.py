from unittest.mock import patch

from url_analysis.brand_confusion import (
    BRAND_RULES_VERSION,
    detect_brand_confusion,
)
from url_analysis.feature_extractor import FEATURE_NAMES, extract_features
from url_analysis.predictor import predict
from url_analysis.scan_service import analyze_url


def test_detects_simple_ascii_brand_lookalike():
    result = detect_brand_confusion("https://micr0soft.com/login")

    assert result is not None
    assert result["detected"] is True
    assert result["brand"] == "Microsoft"
    assert result["matched_label"] == "micr0soft"
    assert result["rule_version"] == BRAND_RULES_VERSION


def test_does_not_flag_official_brand_domain_or_subdomain():
    assert detect_brand_confusion("https://www.microsoft.com/en-us") is None
    assert detect_brand_confusion("https://login.microsoft.com") is None


def test_does_not_flag_unrelated_domain():
    assert detect_brand_confusion("https://example.com") is None
    assert detect_brand_confusion("https://amazonaws.com") is None


def test_delimited_brand_label_is_advisory_match():
    result = detect_brand_confusion("https://microsoft-login.example")

    assert result is not None
    assert result["brand"] == "Microsoft"
    assert result["matched_label"] == "microsoft-login"


def test_one_edit_brand_match_is_supported():
    result = detect_brand_confusion("https://gogle.example")

    assert result is not None
    assert result["brand"] == "Google"
    assert result["matched_label"] == "gogle"


def test_brand_signal_does_not_change_stable_feature_contract():
    features = extract_features("https://micr0soft.com")

    assert tuple(features) == FEATURE_NAMES
    assert len(features) == 20


def test_predictor_adds_brand_reason_without_changing_model_input():
    features = extract_features("https://micr0soft.com")

    with patch("url_analysis.predictor.MODEL_PATH") as model_path:
        model_path.exists.return_value = False
        verdict, confidence, reasons = predict(features, url="https://micr0soft.com")

    assert verdict == "suspicious"
    assert 0 <= confidence <= 1
    assert reasons[0].startswith("The hostname resembles Microsoft")


def test_scan_response_exposes_non_network_brand_metadata():
    with patch("url_analysis.scan_service._persist_scan"):
        result = analyze_url("https://micr0soft.com")

    explanation = result["explanations"]
    assert explanation["network_accessed"] is False
    assert explanation["brand_rules_version"] == BRAND_RULES_VERSION
    assert explanation["brand_confusion"]["brand"] == "Microsoft"
    assert explanation["brand_confusion"]["detected"] is True


def test_brand_detection_does_not_perform_network_io(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network resolver should not be called")

    monkeypatch.setattr("socket.getaddrinfo", fail_if_called)
    result = detect_brand_confusion("https://micr0soft.com")

    assert result is not None

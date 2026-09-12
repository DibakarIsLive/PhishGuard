from vision.feature_extractor import extract_features
from vision.predictor import predict


def test_ip_and_at_symbol_are_detected():
    features = extract_features("http://192.168.1.10/login@evil.example/verify")
    assert features["has_ip_address"] == 1
    assert features["has_at_symbol"] == 1


def test_high_risk_url_is_flagged():
    result = predict("http://192.168.1.10/secure-login/verify-account")
    assert result["verdict"] == "phishing"

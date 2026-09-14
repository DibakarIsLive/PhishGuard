from unittest.mock import patch

from url_analysis.feature_extractor import extract_features
from url_analysis.predictor import _validate_model, model_status, predict


class CompatibleModel:
    feature_names_in_ = None
    n_features_in_ = 20

    def predict(self, values):
        return [0]

    def predict_proba(self, values):
        return [[0.8, 0.2]]


class IncompatibleModel:
    n_features_in_ = 2

    def predict(self, values):
        return [1]


def test_heuristic_prediction_returns_bounded_result():
    verdict, confidence, reasons = predict(extract_features("https://example.com/login"))

    assert verdict in {"legitimate", "suspicious", "phishing"}
    assert 0 <= confidence <= 1
    assert reasons


def test_compatible_optional_model_can_be_used():
    features = extract_features("https://example.com")
    with patch("url_analysis.predictor.MODEL_PATH") as model_path, patch(
        "url_analysis.predictor.joblib.load", return_value=CompatibleModel()
    ):
        model_path.exists.return_value = True
        verdict, confidence, reasons = predict(features)

    assert verdict == "legitimate"
    assert confidence == 0.8
    assert reasons == ["Optional trained model prediction"]


def test_compatible_model_keeps_brand_signal_as_advisory_reason():
    features = extract_features("https://micr0soft.com")
    with patch("url_analysis.predictor.MODEL_PATH") as model_path, patch(
        "url_analysis.predictor.joblib.load", return_value=CompatibleModel()
    ):
        model_path.exists.return_value = True
        verdict, confidence, reasons = predict(features, url="https://micr0soft.com")

    assert verdict == "legitimate"
    assert confidence == 0.8
    assert reasons[0].startswith("The hostname resembles Microsoft")
    assert reasons[-1] == "Optional trained model prediction"


def test_incompatible_optional_model_falls_back_to_heuristics():
    features = extract_features("https://example.com")
    with patch("url_analysis.predictor.MODEL_PATH") as model_path, patch(
        "url_analysis.predictor.joblib.load", return_value=IncompatibleModel()
    ):
        model_path.exists.return_value = True
        verdict, confidence, reasons = predict(features)

    assert verdict == "legitimate"
    assert 0 <= confidence <= 1
    assert reasons == ["No strong phishing indicators were found"]


def test_model_status_reports_fallback_when_artifact_is_absent():
    with patch("url_analysis.predictor.MODEL_PATH") as model_path:
        model_path.exists.return_value = False
        status = model_status()

    assert status["status"] == "fallback"
    assert status["available"] is False
    assert status["feature_count"] == 20


def test_model_contract_rejects_wrong_feature_count():
    try:
        _validate_model(IncompatibleModel())
    except ValueError as exc:
        assert "feature count" in str(exc)
    else:
        raise AssertionError("Expected incompatible model to be rejected")

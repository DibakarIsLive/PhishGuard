from url_analysis.feature_extractor import FEATURE_NAMES, extract_features


def test_feature_order_is_stable():
    features = extract_features("https://example.com/login")
    assert tuple(features) == FEATURE_NAMES
    assert features["has_https"] == 1


def test_ip_url_is_flagged():
    features = extract_features("http://192.168.1.10/login")
    assert features["has_ip_address"] == 1

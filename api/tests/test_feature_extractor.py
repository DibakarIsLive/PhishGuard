from url_analysis.feature_extractor import FEATURE_NAMES, FEATURE_VERSION, extract_features


def test_feature_order_is_stable():
    features = extract_features("https://example.com/login")

    assert tuple(features) == FEATURE_NAMES
    assert len(features) == 20
    assert features["has_https"] == 1
    assert FEATURE_VERSION == "url-features-v1"


def test_ip_url_is_flagged():
    features = extract_features("http://192.168.1.10/login")

    assert features["has_ip_address"] == 1


def test_invalid_ipv4_shaped_hostname_is_not_treated_as_an_ip():
    features = extract_features("http://999.999.999.999/login")

    assert features["has_ip_address"] == 0


def test_feature_extraction_does_not_change_with_surrounding_whitespace():
    plain = extract_features("https://example.com/path")
    padded = extract_features("  https://example.com/path  ")

    assert padded == plain

import pytest

from url_analysis.url_validation import URLValidationError, normalize_url


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "not a url",
        "ftp://example.com/file",
        "https://example.com/has space",
        "https://example.com\\path",
        "https://example.com:99999/",
    ],
)
def test_normalize_url_rejects_unsupported_or_malformed_values(value):
    with pytest.raises(URLValidationError):
        normalize_url(value)


def test_normalize_url_preserves_trimmed_input_without_network_access():
    assert normalize_url("  example.com/login  ") == "example.com/login"


def test_normalize_url_enforces_configured_length():
    with pytest.raises(URLValidationError, match="10 characters"):
        normalize_url("example.com", max_length=10)

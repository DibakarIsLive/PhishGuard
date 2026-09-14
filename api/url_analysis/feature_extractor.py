"""Deterministic, network-free features derived from a URL string."""

from __future__ import annotations

import ipaddress
import math
import re
from urllib.parse import urlparse


FEATURE_VERSION = "url-features-v1"
FEATURE_NAMES = (
    "url_length",
    "hostname_length",
    "dot_count",
    "hyphen_count",
    "at_count",
    "question_count",
    "equals_count",
    "slash_count",
    "digit_ratio",
    "has_ip_address",
    "has_https",
    "has_suspicious_tld",
    "has_punycode",
    "subdomain_count",
    "path_length",
    "query_length",
    "entropy",
    "has_login_keyword",
    "has_redirect_symbol",
    "has_encoded_character",
)

SUSPICIOUS_TLDS = {
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".top",
    ".click",
    ".work",
    ".zip",
    ".review",
}
LOGIN_KEYWORDS = re.compile(
    r"login|verify|account|secure|update|signin|password",
    re.IGNORECASE,
)


def _entropy(value: str) -> float:
    if not value:
        return 0.0

    counts = {character: value.count(character) for character in set(value)}
    length = len(value)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def _has_ipv4_address(hostname: str) -> int:
    try:
        return int(ipaddress.ip_address(hostname).version == 4)
    except ValueError:
        return 0


def extract_features(url: str) -> dict[str, float | int]:
    """Return the stable Phase 1 feature contract for ``url``.

    This function only parses the supplied string. It never performs HTTP,
    DNS, TLS, browser, or third-party reputation operations.
    """
    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else f"http://{raw}")
    host = parsed.hostname or ""
    host_lower = host.lower()

    features = {
        "url_length": len(raw),
        "hostname_length": len(host),
        "dot_count": raw.count("."),
        "hyphen_count": raw.count("-"),
        "at_count": raw.count("@"),
        "question_count": raw.count("?"),
        "equals_count": raw.count("="),
        "slash_count": raw.count("/"),
        "digit_ratio": sum(character.isdigit() for character in raw)
        / max(len(raw), 1),
        "has_ip_address": _has_ipv4_address(host),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_suspicious_tld": int(
            any(host_lower.endswith(tld) for tld in SUSPICIOUS_TLDS)
        ),
        "has_punycode": int("xn--" in host_lower),
        "subdomain_count": max(host.count(".") - 1, 0),
        "path_length": len(parsed.path),
        "query_length": len(parsed.query),
        "entropy": round(_entropy(raw), 5),
        "has_login_keyword": int(bool(LOGIN_KEYWORDS.search(raw))),
        "has_redirect_symbol": int("//" in parsed.path or "@" in raw),
        "has_encoded_character": int("%" in raw),
    }

    # Constructing the dictionary in FEATURE_NAMES order is deliberate: the
    # optional model boundary consumes this exact sequence.
    return {name: features[name] for name in FEATURE_NAMES}

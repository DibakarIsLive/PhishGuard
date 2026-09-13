from urllib.parse import urlparse
import math
import re

FEATURE_NAMES = ("url_length", "hostname_length", "dot_count", "hyphen_count", "at_count", "question_count", "equals_count", "slash_count", "digit_ratio", "has_ip_address", "has_https", "has_suspicious_tld", "has_punycode", "subdomain_count", "path_length", "query_length", "entropy", "has_login_keyword", "has_redirect_symbol", "has_encoded_character")
SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click", ".work", ".zip", ".review"}


def _entropy(value):
    if not value:
        return 0.0
    counts = {char: value.count(char) for char in set(value)}
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def extract_features(url):
    parsed = urlparse(url if "://" in url else f"http://{url}")
    host = parsed.hostname or ""
    raw = url.strip()
    return {
        "url_length": len(raw), "hostname_length": len(host), "dot_count": raw.count("."),
        "hyphen_count": raw.count("-"), "at_count": raw.count("@"), "question_count": raw.count("?"),
        "equals_count": raw.count("="), "slash_count": raw.count("/"),
        "digit_ratio": sum(char.isdigit() for char in raw) / max(len(raw), 1),
        "has_ip_address": int(bool(re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", host))),
        "has_https": int(parsed.scheme.lower() == "https"),
        "has_suspicious_tld": int(any(host.lower().endswith(tld) for tld in SUSPICIOUS_TLDS)),
        "has_punycode": int("xn--" in host.lower()), "subdomain_count": max(host.count(".") - 1, 0),
        "path_length": len(parsed.path), "query_length": len(parsed.query), "entropy": round(_entropy(raw), 5),
        "has_login_keyword": int(bool(re.search(r"login|verify|account|secure|update|signin|password", raw, re.I))),
        "has_redirect_symbol": int("//" in parsed.path or "@" in raw), "has_encoded_character": int("%" in raw),
    }

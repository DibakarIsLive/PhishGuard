"""Fast, network-free feature extraction for safe URL analysis."""
import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_WORDS = {"account", "authenticate", "banking", "confirm", "credential", "login", "password", "secure", "signin", "update", "verify", "wallet"}
SUSPICIOUS_TLDS = {".biz", ".click", ".gq", ".info", ".link", ".live", ".ru", ".tk", ".top", ".work", ".xyz"}
SHORTENERS = {"bit.ly", "cutt.ly", "is.gd", "rb.gy", "rebrand.ly", "shorturl.at", "tinyurl.com", "t.co"}


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    total = len(text)
    return -sum((count / total) * math.log2(count / total) for count in Counter(text).values())


def extract_features(url: str) -> dict:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = (parsed.hostname or "").lower()
    path_query = f"{parsed.path}?{parsed.query}".lower()
    try:
        has_ip = int(bool(ipaddress.ip_address(host)))
    except ValueError:
        has_ip = 0
    words = re.findall(r"[a-z]+", f"{host} {path_query}")
    suffix = "." + host.rsplit(".", 1)[-1] if "." in host else ""
    return {
        "url_length": len(url), "domain_length": len(host), "path_length": len(parsed.path),
        "dot_count": url.count("."), "hyphen_count": url.count("-"), "digit_count": sum(char.isdigit() for char in url),
        "special_char_count": sum(url.count(char) for char in "@_?=&%"), "subdomain_count": max(0, len(host.split(".")) - 2),
        "has_at_symbol": int("@" in url), "has_ip_address": has_ip, "uses_https": int(parsed.scheme == "https"),
        "has_punycode": int("xn--" in host), "has_shortener": int(host in SHORTENERS),
        "suspicious_tld": int(suffix in SUSPICIOUS_TLDS), "suspicious_keyword_count": sum(word in SUSPICIOUS_WORDS for word in words),
        "url_entropy": round(_entropy(url.lower()), 3), "encoded_character_count": len(re.findall(r"%[0-9a-fA-F]{2}", url)),
        "double_slash_in_path": int("//" in parsed.path), "has_port": int(parsed.port is not None),
        "query_parameter_count": len([item for item in parsed.query.split("&") if item]),
    }

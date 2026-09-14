"""Small, local brand-confusion checks for URL hostnames.

The rules are intentionally explicit and incomplete. They provide an advisory
signal for common look-alike hostnames without claiming comprehensive
brand-protection or threat-intelligence coverage.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit


BRAND_RULES_VERSION = "local-brand-rules-v1"


@dataclass(frozen=True)
class BrandRule:
    """One locally configured brand name and its known official domains."""

    display_name: str
    canonical_name: str
    official_domains: tuple[str, ...]


# This is a deliberately small, reviewable allowlist rather than a complete
# list of brands or domains. Additions should be accompanied by tests.
BRAND_RULES = (
    BrandRule("Amazon", "amazon", ("amazon.com", "amazon.in")),
    BrandRule("Apple", "apple", ("apple.com", "icloud.com")),
    BrandRule("Facebook", "facebook", ("facebook.com",)),
    BrandRule("Google", "google", ("google.com", "google.co.in")),
    BrandRule("Instagram", "instagram", ("instagram.com",)),
    BrandRule("Microsoft", "microsoft", ("microsoft.com", "microsoftonline.com")),
    BrandRule("Netflix", "netflix", ("netflix.com",)),
    BrandRule("PayPal", "paypal", ("paypal.com",)),
    BrandRule("WhatsApp", "whatsapp", ("whatsapp.com",)),
)

# Common character substitutions seen in simple look-alike hostnames. This is
# not a Unicode homoglyph detector and intentionally does not claim to cover it.
_CONFUSABLE_TRANSLATION = str.maketrans(
    {
        "0": "o",
        "1": "l",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
    }
)


def _hostname(url: str) -> str:
    parsed = urlsplit(url if "://" in url else f"http://{url}")
    try:
        return (parsed.hostname or "").strip(".").lower()
    except ValueError:
        return ""


def _compact_label(label: str) -> str:
    return label.replace("-", "").replace("_", "").translate(_CONFUSABLE_TRANSLATION)


def _edit_distance(left: str, right: str) -> int:
    """Return Levenshtein distance without external dependencies."""
    if len(left) < len(right):
        left, right = right, left
    if not right:
        return len(left)

    previous = list(range(len(right) + 1))
    for left_index, left_character in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_character in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_character != right_character),
                )
            )
        previous = current
    return previous[-1]


def _is_official_hostname(hostname: str, rule: BrandRule) -> bool:
    return any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in rule.official_domains
    )


def _matches_brand_label(label: str, rule: BrandRule) -> bool:
    normalized = label.lower()
    compact = _compact_label(normalized)
    canonical = rule.canonical_name

    # A digit substitution or separator removal produces the canonical name.
    if compact == canonical and normalized != canonical:
        return True

    # An exact brand label outside its known official domains is suspicious as
    # a possible impersonation, while ordinary words such as "amazonaws" are
    # not matched by this branch.
    if normalized == canonical:
        return True

    # Match an explicit hyphen/underscore-delimited brand token, for example
    # "microsoft-login". Do not treat arbitrary substrings as brand matches.
    tokens = [token for token in normalized.replace("_", "-").split("-") if token]
    if canonical in tokens:
        return True

    # Catch a simple one-character omission or substitution such as "gogle".
    return len(normalized) >= 4 and _edit_distance(normalized, canonical) == 1


def detect_brand_confusion(url: str) -> dict[str, str | bool] | None:
    """Return a preliminary local brand-confusion signal, if one is found.

    The function parses only the supplied URL string. It does not resolve a
    hostname, request a page, consult a reputation service, or use a complete
    public-suffix database.
    """
    hostname = _hostname(url)
    if not hostname:
        return None

    labels = [label for label in hostname.split(".") if label and label != "www"]
    for rule in BRAND_RULES:
        if _is_official_hostname(hostname, rule):
            continue
        for label in labels:
            if _matches_brand_label(label, rule):
                return {
                    "detected": True,
                    "rule_version": BRAND_RULES_VERSION,
                    "brand": rule.display_name,
                    "matched_label": label,
                    "hostname": hostname,
                    "reason": (
                        f"The hostname resembles {rule.display_name} but is not "
                        "one of the locally configured official domains"
                    ),
                }

    return None

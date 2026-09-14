"""Local-only validation and normalization for submitted URL strings."""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlsplit


ALLOWED_SCHEMES = {"http", "https"}


class URLValidationError(ValueError):
    """Raised when a submitted value is not a structurally usable URL."""


def normalize_url(value: str, max_length: Optional[int] = None) -> str:
    """Trim and validate a URL without contacting its destination.

    A missing scheme is accepted for the Phase 1 UI and is supplied only to the
    parser. The returned value preserves the user's trimmed input; no network
    request, DNS lookup, redirect, or browser operation occurs here.
    """
    if not isinstance(value, str):
        raise URLValidationError("Enter a URL as text.")

    normalized = value.strip()
    if not normalized:
        raise URLValidationError("Enter a URL with a domain name.")

    if max_length is not None and len(normalized) > max_length:
        raise URLValidationError(f"URL must be {max_length} characters or fewer.")

    if any(character.isspace() for character in normalized):
        raise URLValidationError("URL cannot contain whitespace inside the address.")

    # Backslashes are ambiguous between browser, filesystem, and URL parsing
    # rules. Rejecting them keeps the Phase 1 contract deterministic.
    if "\\" in normalized:
        raise URLValidationError("URL must use forward slashes.")

    candidate = normalized if "://" in normalized else f"http://{normalized}"

    try:
        parsed = urlsplit(candidate)
        hostname = parsed.hostname
        # Accessing .port performs range and syntax validation in urllib.
        parsed.port
    except ValueError as exc:
        raise URLValidationError("Enter a valid URL with a domain name.") from exc

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise URLValidationError("Only HTTP and HTTPS URLs are supported.")

    if not parsed.netloc or not hostname:
        raise URLValidationError("Enter a valid URL with a domain name.")

    if len(hostname) > 253:
        raise URLValidationError("The hostname is too long.")

    return normalized

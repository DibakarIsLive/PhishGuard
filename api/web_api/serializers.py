"""HTTP request serializers for the Phase 1 API."""

from django.conf import settings
from rest_framework import serializers

from url_analysis.url_validation import URLValidationError, normalize_url


class ScanSerializer(serializers.Serializer):
    url = serializers.CharField(
        max_length=settings.MAX_URL_LENGTH,
        trim_whitespace=True,
        allow_blank=False,
    )

    def validate_url(self, value: str) -> str:
        try:
            return normalize_url(value, max_length=settings.MAX_URL_LENGTH)
        except URLValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc

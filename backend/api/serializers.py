from rest_framework import serializers


class URLCheckSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=2048, trim_whitespace=True)

    def validate_url(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Enter a URL to scan.")
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        from urllib.parse import urlparse
        if not urlparse(value).hostname:
            raise serializers.ValidationError("Enter a valid website address.")
        return value


class BatchCheckSerializer(serializers.Serializer):
    urls = serializers.ListField(child=serializers.CharField(max_length=2048), min_length=1, max_length=100)


class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(".csv"):
            raise serializers.ValidationError("Upload a CSV file only.")
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("CSV must be smaller than 50 MB for this demo.")
        return value

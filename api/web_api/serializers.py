from rest_framework import serializers


class ScanSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=2048, trim_whitespace=True)

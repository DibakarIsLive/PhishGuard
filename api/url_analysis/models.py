from datetime import datetime, timezone
from mongoengine import DateTimeField, DictField, Document, FloatField, StringField


class Scan(Document):
    url = StringField(required=True)
    verdict = StringField(required=True, choices=("phishing", "suspicious", "legitimate"))
    confidence = FloatField(required=True)
    features = DictField()
    explanations = DictField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    meta = {"collection": "scans", "ordering": ["-created_at"]}

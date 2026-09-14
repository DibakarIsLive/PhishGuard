"""MongoEngine documents used by the Phase 1 scan-history boundary."""

from datetime import datetime, timezone

from mongoengine import DateTimeField, DictField, Document, FloatField, StringField


class Scan(Document):
    url = StringField(required=True)
    verdict = StringField(required=True, choices=("phishing", "suspicious", "legitimate"))
    confidence = FloatField(required=True, min_value=0.0, max_value=1.0)
    features = DictField(default=dict)
    explanations = DictField(default=dict)
    analyzer_version = StringField(default="phase1-heuristic")
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        "collection": "scans",
        "ordering": ["-created_at"],
    }

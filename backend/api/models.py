from django.db import models


class ScanJob(models.Model):
    STATUS_CHOICES = [("queued", "Queued"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")]
    source_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="queued")
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    phishing_count = models.PositiveIntegerField(default=0)
    legitimate_count = models.PositiveIntegerField(default=0)
    invalid_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class Prediction(models.Model):
    scan_job = models.ForeignKey(ScanJob, null=True, blank=True, on_delete=models.SET_NULL, related_name="predictions")
    url = models.URLField(max_length=2048)
    verdict = models.CharField(max_length=20)
    confidence = models.FloatField()
    risk_score = models.FloatField()
    category = models.CharField(max_length=100, blank=True)
    features = models.JSONField(default=dict)
    explanations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

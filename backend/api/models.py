from django.db import models


class Prediction(models.Model):
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

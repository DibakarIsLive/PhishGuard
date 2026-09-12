from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health), path("check-url/", views.check_url), path("batch-check/", views.batch_check),
    path("predictions/", views.predictions), path("stats/", views.stats),
]

from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health), path("check-url/", views.check_url), path("batch-check/", views.batch_check), path("upload-csv/", views.upload_csv), path("bulk-jobs/<int:job_id>/", views.bulk_job_status),
    path("predictions/", views.predictions), path("stats/", views.stats),
]

from django.urls import include, path
from web_api.views import ApiRootView

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("api/", include("web_api.urls")),
]

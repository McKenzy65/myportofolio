from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("certifications/", api_views.certification_list, name="certification-list"),
]

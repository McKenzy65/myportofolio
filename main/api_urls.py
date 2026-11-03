from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("certifications/", api_views.certification_list, name="certification-list"),
    path(
        "certifications/<int:certification_id>/",
        api_views.certification_detail,
        name="certification-detail",
    ),
    path(
        "certifications/<int:certification_id>/star/",
        api_views.certification_star,
        name="certification-star",
    ),
]

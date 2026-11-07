from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("experiences/", api_views.experience_list, name="experience-list"),
    path(
        "experiences/<uuid:experience_id>/",
        api_views.experience_detail,
        name="experience-detail",
    ),
    path(
        "experiences/<uuid:experience_id>/star/",
        api_views.experience_star,
        name="experience-star",
    ),
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

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from main import api_views

app_name = "api"

urlpatterns = [
    path("auth/token/", obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", api_views.api_logout, name="api_logout"),
    path("projects/", api_views.project_list, name="project-list"),
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

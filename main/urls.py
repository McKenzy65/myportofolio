from django.urls import path
from main.views import (
    show_main,
    show_certifications,
    create_certification,
    edit_certification,
    delete_certification,
    get_certifications_json,
    get_experiences_json,
    register,
    login_user,
    logout_user,
)

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('certifications/', show_certifications, name='show_certifications'),
    path("certifications/add/", create_certification, name="create_certification"),
    path("certifications/<int:certification_id>/delete/", delete_certification, name="delete_certification"), 
    path("api/certifications/", get_certifications_json, name="get_certifications_json"),
    path("api/experiences/", get_experiences_json, name="get_experiences_json"),
    path("certifications/<int:certification_id>/edit/", edit_certification, name="edit_certification"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

]

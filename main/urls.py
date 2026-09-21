from django.urls import path
from main.views import show_main, show_certifications, create_certification, delete_certification, get_certifications_json, edit_certification

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('certifications/', show_certifications, name='show_certifications'),
    path("certifications/add/", create_certification, name="create_certification"),
    path("certifications/<int:certification_id>/delete/", delete_certification, name="delete_certification"), 
    path("api/certifications/", get_certifications_json, name="get_certifications_json"),
    path("certifications/<int:certification_id>/edit/", edit_certification, name="edit_certification"), 
]

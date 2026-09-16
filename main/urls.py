from django.urls import path
from main.views import show_main, show_certifications, create_certification, delete_certification

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('certifications/', show_certifications, name='show_certifications'),
    path("certifications/add/", create_certification, name="create_certification"),
    path("certifications/<int:certification_id>/delete/", delete_certification, name="delete_certification"), 
]

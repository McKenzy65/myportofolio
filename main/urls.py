from django.urls import path
from main.views import show_main, show_certifications

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('certifications/', show_certifications, name='show_certifications'),
]
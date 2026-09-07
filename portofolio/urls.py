from django.contrib import admin
from django.urls import path
from portofolio.views import show_main
from portofolio.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', show_main, name='show_main'),
]
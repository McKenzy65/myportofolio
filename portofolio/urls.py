from django.contrib import admin
from django.urls import path, include
# import view kamu di sini jika langsung dipanggil

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), 
]
from django.contrib import admin
from django.urls import path, include
#from accounts import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('accounts.urls')),
    path("", include('employee.urls')),
    path("", include('jabatan.urls')),   
    path("", include('dept.urls')),   
]

from django.urls import path
from . import views
from django.conf import settings
from django.http import FileResponse
from django.contrib import messages
from django.shortcuts import redirect
import os

def download_missing_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "reports", filename)
    if os.path.exists(file_path):
        file = open(file_path, "rb")
        response = FileResponse(file, as_attachment=True, filename=filename)
        return response
    else:
        messages.error(request, "❌ File tidak ditemukan.")
        return redirect("machine_list")

urlpatterns = [
    path("machine/", views.machine_list, name="machine_list"),
    path("add/", views.machine_create, name="machine_create"),
    path("<int:pk>/edit/", views.machine_edit, name="machine_edit"),
    path("<int:pk>/connect/", views.machine_connect, name="machine_connect"),
    path("<int:pk>/toggle/", views.machine_toggle_connect, name="machine_toggle_connect"),
    path("<int:pk>/confirm-delete/", views.machine_confirm_delete, name="machine_confirm_delete"),
    path("<int:pk>/delete/", views.machine_delete, name="machine_delete"),
    path("<int:pk>/pull-day-modal/", views.machine_pull_day_modal, name="machine_pull_day_modal"),
    path("<int:pk>/pull-day/", views.machine_pull_day, name="machine_pull_day"),
    path("missing/<str:filename>/", download_missing_file, name="download_missing_file"),
    path("<int:pk>/sync-users/", views.machine_sync_users, name="machine_sync_users"),
]

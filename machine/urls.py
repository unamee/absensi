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
    path("machine/add/", views.machine_create, name="machine_create"),
    path("machine/<int:pk>/edit/", views.machine_edit, name="machine_edit"),
    path("machine/<int:pk>/connect/", views.machine_connect, name="machine_connect"),
    path("machine/<int:pk>/toggle/", views.machine_toggle_connect, name="machine_toggle_connect"),
    path("machine/<int:pk>/confirm-delete/", views.machine_confirm_delete, name="machine_confirm_delete"),
    path("machine/<int:pk>/delete/", views.machine_delete, name="machine_delete"),

    # 🔽 Modal tarik data harian
    path("machine/<int:pk>/pull-day-modal/", views.machine_pull_day_modal, name="machine_pull_day_modal"),
    path("machine/<int:pk>/pull-day/", views.machine_pull_day, name="machine_pull_day"),

    # 🔽 Modal tarik data range tanggal
    path("machine/<int:pk>/pull-range-modal/", views.machine_pull_range_modal, name="machine_pull_range_modal"),
    path("machine/<int:pk>/pull-range/", views.machine_pull_range, name="machine_pull_range"),

    # 🔽 Fitur lainnya
    path("machine/missing/<str:filename>/", download_missing_file, name="download_missing_file"),
    path("machine/<int:pk>/sync-users/", views.machine_sync_users, name="machine_sync_users"),

    path("machine/qr-attendance/", views.qr_attendance_form, name="qr_attendance_form"),
    path("machine/qr-attendance/submit/", views.qr_attendance_submit, name="qr_attendance_submit"),
]

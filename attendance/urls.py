from django.urls import path
from . import views, views_report

urlpatterns = [
    path("attendance/", views.attendance_list, name="attendance_list"),
    path('attendance/export-excel/', views.attendance_export_excel, name='attendance_export_excel'),
    path("attendance/report/", views_report.attendance_report, name="attendance_report"),
]

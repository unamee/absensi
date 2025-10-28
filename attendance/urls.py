from django.urls import path
from . import views

urlpatterns = [
    path("attendance/", views.attendance_list, name="attendance_list"),
    path('attendance/export-excel/', views.attendance_export_excel, name='attendance_export_excel'),
]

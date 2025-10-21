from employee import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("employee/", views.employee_list, name="employee"),
    path("create-employee/", views.create_employee, name="create_employee"),
    path("employee/<int:emp_id>/update/", views.employee_update, name="update-employee"),
    path("employee/<int:emp_id>/", views.employee_info, name="info-employee"),
    path('jabatan/delete-employee/<int:emp_id>/', views.delete_employee, name='delete-employee'),

    path("dashboard/", views.dashboard, name="dashboard-employee"),
    path("dashboard/out-list/", views.out_list, name="out_list"),
    path("dashboard/qr-scan/", views.qr_scan, name="qr_scan"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

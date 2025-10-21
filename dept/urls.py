from dept import views
from django.urls import path

urlpatterns = [
    path("dept/", views.dept, name="dept"),
    path("dept/create-dept/", views.create_dept, name="create_dept"),
    path('dept/update-dept/<int:dept_id>/', views.update_dept, name='update-dept'),  
    path('dept/delete-dept/<int:dept_id>/', views.delete_dept, name='delete-dept'),
]

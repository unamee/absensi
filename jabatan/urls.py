from jabatan import views
from django.urls import path

urlpatterns = [
    path("jabatan/", views.jabatan, name="jabatan"),
    path("jabatan/create-jabatan/", views.create_jabatan, name="create_jabatan"),
    path('jabatan/update-jabatan/<int:jbt_id>/', views.update_jabatan, name='update-jabatan'),  
    path('jabatan/delete-jabatan/<int:jbt_id>/', views.delete_jabatan, name='delete-jabatan'),
]

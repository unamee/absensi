from django.urls import path
from . import views

urlpatterns = [
    path('shift/', views.shift_list, name='shift_list'),
    path('shift/add/', views.shift_create, name='shift_create'),
    path('shift/<int:pk>/edit/', views.shift_edit, name='shift_edit'),
    path('shift/<int:pk>/delete/', views.shift_delete, name='shift_delete'),
]

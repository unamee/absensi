from django.contrib import admin
from django.urls import path
from accounts import views

urlpatterns = [
    #path("", views.login_view, name="login"),
    #path("logout/", views.logout_view, name="logout"),
    #path("dashboard/", views.dashboard, name="dashboard"),

     # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard + Absensi
    path("", views.dashboard, name="dashboard"),
    path("checkin/", views.checkin, name="checkin"),
    path("checkout/", views.checkout, name="checkout"),    
]

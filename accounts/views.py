from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .utils import login_required_nocache
from django.utils import timezone
from django.http import HttpResponse
from .models import Attendance

# --- Login ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")  # ✅ always redirect to dashboard
        else:
            return render(request, "accounts/login.html", {"error": "Username atau password salah"})
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# --- Dashboard ---
@login_required_nocache
def dashboard(request):
    return render(request, "accounts/dashboard.html")

# --- Absensi ---
@login_required_nocache
def checkin(request):
    today = timezone.now().date()
    record, created = Attendance.objects.get_or_create(employee=request.user, date=today)
    if not record.check_in:
        record.check_in = timezone.now().time()
        record.save()
    return HttpResponse(f'<div class="alert alert-success">Check-in: {record.check_in}</div>')

@login_required_nocache
def checkout(request):
    today = timezone.now().date()
    record, created = Attendance.objects.get_or_create(employee=request.user, date=today)
    if not record.check_out:
        record.check_out = timezone.now().time()
        record.save()
    return HttpResponse(f'<div class="alert alert-danger">Check-out: {record.check_out}</div>')


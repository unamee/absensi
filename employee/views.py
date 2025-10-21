import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Employee, BreakLog
from accounts.utils import login_required_nocache
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .utils import generate_qr_code
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


@login_required_nocache
def dashboard(request):
    return render(request, "employee/dashboard.html")


@login_required_nocache
def out_list(request):
    logs = BreakLog.objects.filter(in_time__isnull=True)
    return render(request, "employee/partials/out_list.html", {"logs": logs})

@csrf_exempt  # Karena HTMX post langsung tanpa form CSRF token
@login_required_nocache
def qr_scan(request):
    qr_data = request.POST.get("qr_data", "").strip()

    try:
        employee = Employee.objects.get(id_karyawan=qr_data)
    except Employee.DoesNotExist:
        return JsonResponse({"error": "❌ QR Code tidak dikenali."}, status=400)

    # Cek apakah karyawan sedang keluar
    active_log = BreakLog.objects.filter(employee=employee, in_time__isnull=True).first()

    if active_log:
        # berarti dia masuk kembali
        active_log.in_time = timezone.now()
        active_log.save()
        message = f"✅ {employee.user.get_full_name()} telah kembali ke kantor!"
    else:
        # buat log baru (keluar)
        BreakLog.objects.create(employee=employee, out_time=timezone.now())
        message = f"🚶 {employee.user.get_full_name()} keluar kantor."

    return HttpResponse(f"<div class='alert alert-success text-center'>{message}</div>")


@login_required_nocache
def create_employee(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        id_karyawan = request.POST.get("id_karyawan", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        # Cek jika username sudah ada
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan!")
            return redirect("employee")
        else:
            # 1️⃣ Buat user dulu di tabel auth_user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            # 2️⃣ Baru buat employee terkait
            employee = Employee.objects.create(user=user, id_karyawan=id_karyawan)
            messages.success(request, f"Employee {user.username} berhasil dibuat!")
            return redirect("employee")
    return render(request, "employee/employee_form.html")


@login_required_nocache
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "employee/employee_list.html", {"employees": employees})


@login_required_nocache
def employee_update(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    user = employee.user

    if request.method == "POST":
        id_karyawan = request.POST.get("id_karyawan", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        photo = request.FILES.get("photo")

        if id_karyawan != employee.id_karyawan:
            if employee.qr_code and os.path.isfile(employee.qr_code.path):
                os.remove(employee.qr_code.path)

            employee.id_karyawan = id_karyawan
            generate_qr_code(employee)

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password:
            user.set_password(password)

        user.save()

        if photo:
            employee.photo = photo

        employee.save()
        messages.success(
            request, "✅ Employee updated successfully with resized photo!"
        )
        return redirect("employee")

    return render(request, "employee/partials/employee_update.html", {"employee": user})


# Delete Jabatan
@login_required_nocache
def delete_employee(request, emp_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, id=emp_id)
        employee.delete()

        user = get_object_or_404(User, id=employee.user_id)
        user.delete()

        messages.success(request, f"Employee {user.username} berhasil dihapus!")
        # return redirect('employee_list')

        employee = Employee.objects.all()
        # return render(
        #     request, "employee/partials/employee_table.html", {"employee": employee}
        # )
        return render(request, "employee/employee_list.html", {"employees": employee})

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required_nocache
def print_qr(request, id_karyawan):
    employee = get_object_or_404(Employee, id_karyawan=id_karyawan)
    return render(request, "employee/print_qr.html", {"employee": employee})


@login_required_nocache
def employee_info(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    user = employee.user
    return render(request, "employee/employee_info.html", {"employee": user})


@login_required_nocache
def scan_qr(request):
    emp_id = request.GET.get("qrcode")
    employee = get_object_or_404(Employee, employee_id=emp_id)

    # cek apakah sedang di luar
    current_log = BreakLog.objects.filter(
        employee=employee, in_time__isnull=True
    ).first()

    if current_log:
        # sudah di luar, berarti sekarang masuk
        current_log.in_time = timezone.now()
        current_log.save()
    else:
        # belum keluar, buat log baru
        BreakLog.objects.create(employee=employee)

    return redirect("dashboard")

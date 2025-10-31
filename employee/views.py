import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Employee, BreakLog
from dept.models import Dept
from jabatan.models import Jabatan
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
def break_scan(request):
    #print("📡 Request received:", request.method)
    message = None

    if request.method == "POST":
        qr_code = request.POST.get("qr_code", "").strip()
        #print("🔹 Scanned:", qr_code)

        try:
            emp = Employee.objects.get(id_karyawan=qr_code)
        except Employee.DoesNotExist:
            message = f"❌ ID {qr_code} tidak ditemukan"
            return render(request, "employee/partials/break_message.html", {"message": message})

        # Cek apakah sedang out (belum in)
        existing = BreakLog.objects.filter(employee=emp, in_time__isnull=True).first()
        if existing:
            existing.in_time = timezone.now()
            existing.save()
            message = f"✅ {emp.user.first_name} sudah kembali (In)"
        else:
            BreakLog.objects.create(employee=emp)
            message = f"☕ {emp.user.first_name} keluar istirahat (Out)"

        # Kembalikan hanya pesan (bukan seluruh halaman)
        return render(request, "employee/partials/break_message.html", {"message": message})

    # Jika GET request (pertama kali buka)
    return render(request, "employee/break_scan.html")



@login_required_nocache
def out_list(request):
    logs = BreakLog.objects.filter(in_time__isnull=True).select_related("employee")
    return render(request, "employee/partials/out_list.html", {"logs": logs})


@login_required_nocache
def create_employee(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        id_karyawan = request.POST.get("id_karyawan", "").strip()
        id_pin = request.POST.get("id_pin", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        dept_id = request.POST.get("dept", "").strip()
        jabatan_id = request.POST.get("jabatan", "").strip()
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
            Employee.objects.create(user = user, id_karyawan = id_karyawan, id_pin = id_pin, dept_id = dept_id, jabatan_id = jabatan_id)
            messages.success(request, f"Employee {user.username} berhasil dibuat!")
            return redirect("employee")
    depts = Dept.objects.all()
    jabatan = Jabatan.objects.all()
    context = {
        'depts' : depts,
        'jabatan' : jabatan,
    }
    return render(request, "employee/employee_form.html", context)


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
        id_pin = request.POST.get("id_pin", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        dept_instance = Dept.objects.get(pk=request.POST.get("dept", "").strip())
        jabatan_instance = Jabatan.objects.get(pk=request.POST.get("jabatan", "").strip())
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        photo = request.FILES.get("photo")
        can_qr_attend = bool(request.POST.get("can_qr_attend"))

        # Cek perubahan ID karyawan → regen QR
        if id_karyawan != employee.id_karyawan:
            if employee.qr_code and os.path.isfile(employee.qr_code.path):
                os.remove(employee.qr_code.path)
            employee.id_karyawan = id_karyawan
            generate_qr_code(employee)

        employee.id_pin = id_pin
        employee.dept = dept_instance
        employee.jabatan = jabatan_instance
        employee.can_qr_attend = can_qr_attend

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # ✅ Validasi username unik
        if username != user.username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, f"❌ Username '{username}' sudah digunakan oleh user lain.")
                return redirect("employee_edit", emp_id=employee.id)
            user.username = username

        # ✅ Ganti password jika diisi
        if password:
            user.set_password(password)

        user.save()

        # ✅ Update foto jika diunggah
        if photo:
            employee.photo = photo

        employee.save()

        messages.success(request, f"✅ Data karyawan '{user.username}' berhasil diperbarui.")
        return redirect("employee")

    depts = Dept.objects.all()
    jabatan = Jabatan.objects.all()
    context = {
        'employee': user,
        'depts': depts,
        'jabatan': jabatan,
    }
    return render(request, "employee/partials/employee_update.html", context)


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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Employee
from accounts.utils import login_required_nocache
from django.contrib import messages
from django.contrib.auth.hashers import check_password

@login_required_nocache
def create_employee(request):     
   if request.method == "POST": 
        username = request.POST.get('username', "").strip()
        password = request.POST.get('password', "").strip()
        id_karyawan = request.POST.get("id_karyawan", "").strip() 
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        # Cek jika username sudah ada
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan!")
            return redirect('employee')
        else:
            # 1️⃣ Buat user dulu di tabel auth_user
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
            # 2️⃣ Baru buat employee terkait
            employee = Employee.objects.create(user=user, id_karyawan=id_karyawan)
            messages.success(request, f"Employee {user.username} berhasil dibuat!")
            return redirect('employee')
   return render(request, "employee/employee_form.html")


@login_required_nocache
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "employee/employee_list.html", {"employees": employees})


@login_required_nocache
def employee_update(request, emp_id):    
    employee = get_object_or_404(Employee, id=emp_id)
    user = employee.user  # sudah cukup, tidak perlu get lagi

    # print (emp_id)

    if request.method == "POST":          
        id_karyawan = request.POST.get("id_karyawan", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Jika password kosong tidak berubah password lama
        if password:
            if not user.check_password(password):
                user.set_password(password)

        # 🔍 Cek apakah password masih sama atau berubah
        if password:
            if not user.check_password(password):
                user.set_password(password)  # hanya update kalau password beda
        # kalau kosong, berarti user tidak ingin ubah password

        # Update field lainnya
        user.employee.id_karyawan = id_karyawan
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        user.employee.save()

        messages.success(request, "✅ Employee update successfully!")
        return redirect("employee")

    return render(
        request, "employee/partials/employee_update.html", {"employee": user}
    )

# Delete Jabatan
@login_required_nocache
def delete_employee(request, emp_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, id=emp_id)
        employee.delete()

        user = get_object_or_404(User, id=employee.user_id)
        user.delete()

        messages.success(request, f"Employee {user.username} berhasil dihapus!")
        #return redirect('employee_list')
    
        employee = Employee.objects.all()
        # return render(
        #     request, "employee/partials/employee_table.html", {"employee": employee}
        # )
        return render(request, "employee/employee_list.html", {"employees": employee})

    return JsonResponse({"error": "Invalid request"}, status=400)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from attendance.models import Machine, Connect, Attendance
from employee.models import Employee
from django.views.decorators.http import require_POST
from .forms import MachineForm
from accounts.utils import login_required_nocache
from zk import ZK  # library pyzk untuk koneksi mesin


@login_required_nocache
def machine_list(request):
    machines = Machine.objects.all()
    return render(request, "machine/machine_list.html", {"machines": machines})


@login_required_nocache
def machine_create(request):
    if request.method == "POST":
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Mesin berhasil ditambahkan.")
            return redirect("machine_list")
    else:
        form = MachineForm()
    return render(request, "machine/machine_form.html", {"form": form})


@login_required_nocache
def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == "POST":
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Data mesin diperbarui.")
            machines = Machine.objects.all()
            return render(request, "machine/machine_list.html", {"machines": machines})
    else:
        form = MachineForm(instance=machine)
    return render(request, "machine/machine_form.html", {"form": form})


@login_required_nocache
def machine_confirm_delete(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    html = render_to_string("machine/_confirm_delete.html", {"machine": machine})
    return HttpResponse(html)


@login_required_nocache
def machine_delete(request, pk):
    if request.method == "POST":
        machine = get_object_or_404(Machine, pk=pk)
        machine.delete()
        return HttpResponse("")  # baris dihapus tanpa reload
    return HttpResponse(status=405)


@login_required_nocache
def machine_connect(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    zk = ZK(machine.ip_address, port=4370, timeout=5)
    try:
        conn = zk.connect()
        machine.status = Connect.Connected
        machine.save()
        conn.disconnect()
        messages.success(
            request, f"✅ Terhubung ke mesin {machine.name} ({machine.ip_address})"
        )
    except Exception as e:
        machine.status = Connect.NotConnected
        machine.save()
        messages.error(request, f"❌ Gagal konek: {e}")
    return redirect("machine_list")


@login_required_nocache
def machine_toggle_connect(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    zk = ZK(machine.ip_address, port=4370, timeout=5)

    if machine.status == Connect.Connected:
        machine.status = Connect.NotConnected
        machine.save()
        # messages.info(request, f"🔌 Mesin {machine.name} telah diputuskan.")
    else:
        try:
            conn = zk.connect()
            machine.status = Connect.Connected
            machine.save()
            conn.disconnect()
            # messages.success(request, f"✅ Terhubung ke mesin {machine.name}")
        except Exception as e:
            machine.status = Connect.NotConnected
            machine.save()
            # messages.error(request, f"❌ Gagal konek ke {machine.name}: {e}")

    # Render ulang satu baris saja (update dinamis)
    return render(request, "machine/_machine_row.html", {"m": machine})


@login_required_nocache
def machine_pull_day_modal(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    return render(request, "machine/_pull_day_modal.html", {"machine": machine})


@login_required_nocache
def machine_pull_day(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    zk = ZK(machine.ip_address, port=4370, timeout=5)
    pulled, missing_users = 0, set()
    filename = None
    print("📥 masuk ke machine_pull_day")
    if request.method == "POST":
        print("📅 Tanggal diterima:", request.POST.get("date"))
        try:
            date_str = request.POST.get("date")
            if not date_str:
                messages.error(request, "❌ Harap pilih tanggal.")
                return render(
                    request,
                    "machine/machine_list.html",
                    {"machines": Machine.objects.all()},
                )

            selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            start = timezone.make_aware(
                datetime.combine(selected_date, datetime.min.time())
            )
            end = start + timedelta(days=1)

            conn = zk.connect()
            print("🔌 Connected to:", machine.ip_address)
            logs = conn.get_attendance()
            print("📋 Total logs fetched:", len(logs))

            for log in logs:
                print("📜 Raw log timestamp:", log.timestamp, type(log.timestamp))
                # pastikan semua timestamp jadi timezone aware
                log_time = (
                    timezone.make_aware(log.timestamp)
                    if timezone.is_naive(log.timestamp)
                    else log.timestamp
                )

                if log_time.date() == selected_date.date():
                    print(
                        f"🕒 Log ditemukan: user_id={log.user_id}, timestamp={log_time}"
                    )
                    employee = Employee.objects.filter(id_pin=str(log.user_id)).first()

                    Attendance.objects.get_or_create(
                        machine=machine,
                        user_id=str(log.user_id),
                        timestamp=log_time,
                        defaults={
                            "verify_type": getattr(log, "status", ""),
                            "status": getattr(log, "punch", ""),
                            "employee": employee,
                        },
                    )
                    pulled += 1
                    if not employee:
                        missing_users.add(str(log.user_id))

            conn.disconnect()

            if missing_users:
                reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
                os.makedirs(reports_dir, exist_ok=True)
                filename = f"missing_users_{machine.name}_{date_str}.txt"
                file_path = os.path.join(reports_dir, filename)
                with open(file_path, "w") as f:
                    f.write("Daftar user_id dari mesin yang tidak ditemukan:\n")
                    for uid in sorted(missing_users):
                        f.write(f"{uid}\n")

            messages.success(
                request,
                f"✅ {pulled} data berhasil ditarik dari mesin {machine.name} ({date_str}).",
            )
            if missing_users:
                messages.warning(
                    request,
                    f"⚠️ {len(missing_users)} user tidak ditemukan. Silakan download laporan.",
                )

        except Exception as e:
            messages.error(request, f"❌ Gagal menarik data: {e}")

    # Render ulang tabel mesin sebagai partial (bukan full HTML)
    machines = Machine.objects.all()
    html = render_to_string(
        "machine/_machine_table.html",
        {"machines": machines, "missing_file": filename},
        request,
    )
    return HttpResponse(html)


@login_required_nocache
def machine_sync_users(request, pk):
    machine = get_object_or_404(Machine, pk=pk)

    # ✅ Pastikan mesin terkoneksi
    if machine.status != "Y":
        messages.error(request, f"❌ Mesin {machine.name} belum terkoneksi.")
        return redirect("machine_list")

    try:
        zk = ZK(machine.ip_address, port=4370, timeout=5)
        conn = zk.connect()
        users = conn.get_users()  # ambil semua user di mesin

        imported, skipped = 0, 0

        for u in users:
            user_id = str(u.user_id).strip()
            name = u.name.strip() if u.name else f"User_{user_id}"

            # ❌ Skip jika user_id sudah ada di Employee
            if Employee.objects.filter(id_pin=user_id).exists():
                skipped += 1
                continue

            # ✅ Pastikan id_karyawan unik (gunakan ID mesin)
            new_id_karyawan = f"PIN{user_id}"

            # ✅ Buat user Django dasar (opsional)
            django_user, _ = User.objects.get_or_create(
                username=f"user_{user_id}",
                defaults={
                    "first_name": name,
                    "is_active": True,
                },
            )

            # ✅ Simpan ke Employee dengan id_karyawan unik
            emp = Employee(
                user=django_user,
                id_karyawan=new_id_karyawan,
                id_pin=user_id,
            )
            emp.save()
            imported += 1

        conn.disconnect()
        messages.success(
            request,
            f"✅ Sinkronisasi selesai. {imported} user baru ditambahkan, {skipped} dilewati.",
        )

    except Exception as e:
        messages.error(request, f"❌ Gagal sinkronisasi: {e}")

    return redirect("machine_list")


@login_required_nocache
def machine_pull_range_modal(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    return render(
        request, "machine/machine_pull_range_modal.html", {"machine": machine}
    )


@login_required_nocache
def machine_pull_range(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    zk = ZK(machine.ip_address, port=4370, timeout=5)
    pulled, missing_users = 0, set()
    filename = None

    print("📥 masuk ke machine_pull_range")

    if request.method == "POST":
        start_str = request.POST.get("start_date")
        end_str = request.POST.get("end_date")

        print(f"📅 Range diterima: {start_str} s.d {end_str}")

        # Validasi input
        if not start_str or not end_str:
            messages.error(request, "❌ Harap pilih rentang tanggal.")
            return render(
                request,
                "machine/machine_list.html",
                {"machines": Machine.objects.all()},
            )

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")

            # Pastikan aware timezone
            start = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            )
            end = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

            conn = zk.connect()
            print("🔌 Connected to:", machine.ip_address)
            logs = conn.get_attendance()
            print("📋 Total logs fetched:", len(logs))

            for log in logs:
                log_time = (
                    timezone.make_aware(log.timestamp)
                    if timezone.is_naive(log.timestamp)
                    else log.timestamp
                )

                # ✅ filter hanya log di dalam rentang tanggal
                if start.date() <= log_time.date() <= end.date():
                    employee = Employee.objects.filter(id_pin=str(log.user_id)).first()

                    Attendance.objects.get_or_create(
                        machine=machine,
                        user_id=str(log.user_id),
                        timestamp=log_time,
                        defaults={
                            "verify_type": getattr(log, "status", ""),
                            "status": getattr(log, "punch", ""),
                            "employee": employee,
                        },
                    )
                    pulled += 1
                    if not employee:
                        missing_users.add(str(log.user_id))

            conn.disconnect()

            # Simpan missing user ke file
            if missing_users:
                reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
                os.makedirs(reports_dir, exist_ok=True)
                filename = f"missing_users_{machine.name}_{start_str}_to_{end_str}.txt"
                file_path = os.path.join(reports_dir, filename)
                with open(file_path, "w") as f:
                    f.write("Daftar user_id dari mesin yang tidak ditemukan:\n")
                    for uid in sorted(missing_users):
                        f.write(f"{uid}\n")

            messages.success(
                request,
                f"✅ {pulled} data berhasil ditarik dari mesin {machine.name} ({start_str} s.d {end_str}).",
            )
            if missing_users:
                messages.warning(
                    request,
                    f"⚠️ {len(missing_users)} user tidak ditemukan. Silakan download laporan.",
                )

        except Exception as e:
            messages.error(request, f"❌ Gagal menarik data: {e}")

    # 🔁 Render ulang tabel mesin (HTMX)
    machines = Machine.objects.all()
    html = render_to_string(
        "machine/_machine_table.html",
        {"machines": machines, "missing_file": filename},
        request,
    )
    return HttpResponse(html)


@login_required_nocache
def qr_attendance_form(request):
    return render(request, "machine/QR/qr_attendance_form.html")


@login_required_nocache
@require_POST
def qr_attendance_submit(request):
    qr_value = request.POST.get("qr_value", "").strip()

    if not qr_value:
        return JsonResponse(
            {"status": "error", "message": "QR Code tidak boleh kosong."}
        )

    try:
        employee = Employee.objects.get(id_karyawan=qr_value, can_qr_attend=True)
    except Employee.DoesNotExist:
        return JsonResponse(
            {
                "status": "error",
                "message": "Karyawan tidak ditemukan atau tidak diizinkan absen QR.",
            }
        )

    # Misal machine default di-set id=1
    machine = Machine.objects.first()

    Attendance.objects.create(
        machine=machine,
        employee=employee,
        user_id=employee.id_pin or employee.id_karyawan,
        timestamp=timezone.now(),
        verify_type="QR",
        status="IN",
    )

    return JsonResponse(
        {
            "status": "success",
            "message": f"Absensi berhasil untuk {employee.user.get_full_name()} ({employee.id_karyawan})",
        }
    )

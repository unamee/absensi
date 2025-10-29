from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from attendance.models import Attendance
from employee.models import Employee
from django.utils.timezone import localtime


def attendance_report(request):
    start_str = request.GET.get("start_date")
    end_str = request.GET.get("end_date")

    if start_str and end_str:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    else:
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today

    # ambil semua data absensi dalam range
    logs = Attendance.objects.filter(
        timestamp__date__range=(start_date, end_date)
    ).select_related("employee", "employee__dept", "employee__jabatan")

    # buat struktur data per karyawan per hari
    report = {}
    for log in logs:
        if not log.employee:
            continue
        emp = log.employee
        emp_id = emp.id_karyawan
        name = f"{emp.user.first_name} {emp.user.last_name}".strip()
        dept = emp.dept.nama_dept if emp.dept else "-"
        jabatan = emp.jabatan.nama_jabatan if emp.jabatan else "-"

        if emp_id not in report:
            report[emp_id] = {
                "nama": name,
                "dept": dept,
                "jabatan": jabatan,
                "harian": {},
            }

        local_ts = localtime(log.timestamp)  # ✅ convert ke waktu lokal
        tanggal = local_ts.date()
        jam = local_ts.strftime("%H:%M")

        #tanggal = log.timestamp.date()
        #jam = log.timestamp.strftime("%H:%M")
        # hanya simpan jam pertama dan terakhir per hari
        if tanggal not in report[emp_id]["harian"]:
            report[emp_id]["harian"][tanggal] = {"masuk": jam, "pulang": jam}
        else:
            report[emp_id]["harian"][tanggal]["pulang"] = jam

        if report:
            first_data = next(iter(report.values()))  # ambil elemen pertama dari dict
            tanggal_list = list(first_data["harian"].keys())
        else:
            tanggal_list = []

    # tampilkan ke halaman
    context = {
        "report": report,
        "start_date": start_date,
        "end_date": end_date,
        "tanggal_list": tanggal_list,  # ✅ kirim ke template
    }

    # ✅ Render partial jika via HTMX
    if request.headers.get("HX-Request") and "partial" in request.GET:
        return render(request, "attendance/partial/_attendance_table_report.html", context)

    if request.GET.get("export") == "excel":
        return export_to_excel(report, start_date, end_date)

    return render(request, "attendance/attendance_report.html", context)


def export_to_excel(report, start_date, end_date):
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Absensi"

    # header perusahaan & periode
    ws.merge_cells("A1:I1")
    ws["A1"] = "PT WinnerSumbiri Knitting Factory"
    ws["A1"].font = Font(size=14, bold=True)
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:I2")
    ws["A2"] = (
        f"Periode: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
    )
    ws["A2"].alignment = Alignment(horizontal="center")

    # header kolom
    headers = ["No", "ID Karyawan", "Nama", "Dept", "Jabatan"]
    date_range = []
    current = start_date
    while current <= end_date:
        headers.append(current.strftime("%d-%b"))
        date_range.append(current)
        current += timedelta(days=1)
    headers.extend(["Total Hadir", "Total Alpha"])

    ws.append(headers)

    thin = Side(border_style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # isi data
    for i, (emp_id, data) in enumerate(report.items(), start=1):
        row = [
            i,
            emp_id,
            data["nama"],
            data["dept"],
            data["jabatan"],
        ]
        hadir = 0
        alpha = 0
        for tgl in date_range:
            if tgl in data["harian"]:
                jam_masuk = data["harian"][tgl]["masuk"]
                jam_pulang = data["harian"][tgl]["pulang"]
                row.append(f"{jam_masuk}-{jam_pulang}")
                hadir += 1
            else:
                row.append("A")
                alpha += 1
        row.extend([hadir, alpha])
        ws.append(row)

    # border & alignment
    for row in ws.iter_rows(min_row=4, max_col=len(headers)):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # set lebar kolom
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 15

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Laporan_Absensi_{start_date}_{end_date}.xlsx"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    wb.save(response)
    return response

from django.shortcuts import get_object_or_404, render, redirect
from dept.models import Dept
from accounts.utils import login_required_nocache
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

@login_required_nocache
def dept(request):
    dept = Dept.objects.all().order_by("-id_dept")
    #print(dept)
    return render(request, "dept/dept.html", {"dept": dept})

@login_required_nocache
def create_dept(request):
    if request.method == "POST":  
        nama_dept = request.POST.get("nama_dept", "").strip()
      
        # siapkan HTML form (render ulang)
        form_html = render_to_string("dept/dept_form.html", request=request)

        if Dept.objects.filter(nama_dept=nama_dept).exists():
            oob = '<div id="message-area" class="alert alert-danger">❌ Duplicate Nama dept!</div>'
            return HttpResponse(oob + form_html)

        Dept.objects.create(nama_dept=nama_dept)
        oob = '<div id="message-area" class="alert alert-success">✅ dept berhasil ditambahkan!</div>'
        return HttpResponse(oob + form_html)

    return render(request, "dept/dept_form.html")

@login_required_nocache
def update_dept(request, dept_id):
    dept = get_object_or_404(Dept, id_dept=dept_id)
    if request.method == "POST":
        nama_dept = request.POST.get("nama_dept", "").strip()        
        dept.nama_dept = nama_dept
        dept.save()
        messages.success(request, "✅ Dept update successfully!")
        return redirect("dept")
    return render(request, "dept/partials/dept_update.html", {"dept":dept})

@login_required_nocache
def delete_dept(request, dept_id):
    if request.method == "POST":
        dept = get_object_or_404(Dept, id_dept=dept_id)
        dept.delete()
        dept = Dept.objects.all()
        return render(
            request, "dept/partials/dept_table.html", {"dept": dept}
        )
    return JsonResponse({"error": "Invalid request"}, status=400)
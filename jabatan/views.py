from django.shortcuts import get_object_or_404, render, redirect
from jabatan.models import Jabatan
from accounts.utils import login_required_nocache
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages


@login_required_nocache
def jabatan(request):
    jabatan = Jabatan.objects.all().order_by("-id_jabatan")
    #print(jabatan)
    return render(request, "jabatan/jabatan.html", {"jabatan": jabatan})


@login_required_nocache
def create_jabatan(request):
    if request.method == "POST":  
        kode_jabatan = request.POST.get("kode_jabatan", "").strip()
        nama_jabatan = request.POST.get("nama_jabatan", "").strip()
      
        # siapkan HTML form (render ulang)
        form_html = render_to_string("jabatan/jabatan_form.html", request=request)

        if Jabatan.objects.filter(kode_jabatan=kode_jabatan).exists():
            oob = '<div id="message-area" class="alert alert-danger">❌ Duplicate Kode Jabatan!</div>'
            return HttpResponse(oob + form_html)

        Jabatan.objects.create(kode_jabatan=kode_jabatan, nama_jabatan=nama_jabatan)
        oob = '<div id="message-area" class="alert alert-success">✅ Jabatan berhasil ditambahkan!</div>'
        return HttpResponse(oob + form_html)

    return render(request, "jabatan/jabatan_form.html")

# Update Jabatan
@login_required_nocache
def update_jabatan(request, jbt_id):
    jabatan = get_object_or_404(Jabatan, id_jabatan=jbt_id)
    if request.method == "POST":
        nama_jabatan = request.POST.get("nama_jabatan", "").strip()        
        jabatan.nama_jabatan = nama_jabatan
        jabatan.save()
        messages.success(request, "✅ Jabatan update successfully!")
        return redirect("jabatan")
    return render(request, "jabatan/partials/jabatan_update.html", {"jabatan":jabatan})

# Delete Jabatan
@login_required_nocache
def delete_jabatan(request, jbt_id):
    if request.method == "POST":
        jabatan = get_object_or_404(Jabatan, id_jabatan=jbt_id)
        jabatan.delete()
        jabatan = Jabatan.objects.all()
        return render(
            request, "jabatan/partials/jabatan_table.html", {"jabatan": jabatan}
        )

    return JsonResponse({"error": "Invalid request"}, status=400)
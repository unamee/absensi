from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Shift
from .forms import ShiftForm
from accounts.utils import login_required_nocache

@login_required_nocache
def shift_list(request):
    shifts = Shift.objects.all().order_by('name')
    return render(request, 'shift/shift_list.html', {'shifts': shifts})

@login_required_nocache
def shift_create(request):
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            start = form.cleaned_data['start_time']
            end = form.cleaned_data['end_time']

            # Cek apakah sudah ada shift dengan kombinasi ini
            if Shift.objects.filter(name__iexact=name, start_time=start, end_time=end).exists():
                messages.warning(request, f"⚠️ Shift '{name}' dengan jam {start} - {end} sudah ada.")
                return render(request, 'shift/shift_form.html', {'form': form})

            form.save()
            messages.success(request, f"✅ Shift '{name}' berhasil ditambahkan.")
            return redirect('shift_list')
    else:
        form = ShiftForm()

    return render(request, 'shift/shift_form.html', {'form': form})

@login_required_nocache
def shift_edit(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Shift berhasil diperbarui.")
            return redirect('shift_list')
    else:
        form = ShiftForm(instance=shift)
    return render(request, 'shift/shift_form.html', {'form': form})

@login_required_nocache
def shift_delete(request, pk):
    shift = get_object_or_404(Shift, pk=pk)
    if request.method == "DELETE":
        shift.delete()
        messages.success(request, f"✅ Shift '{shift.name}' berhasil dihapus.")
        shifts = Shift.objects.all()
        return render(request, "shift/shift_list.html", {"shifts": shifts})
    else:
        return redirect('shift_list')

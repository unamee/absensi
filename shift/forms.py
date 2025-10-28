from django import forms
from .models import Shift, ShiftSchedule

class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name', 'start_time', 'end_time', 'tolerance_in', 'tolerance_out']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'end_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['start_time'] = self.instance.start_time.strftime('%H:%M')
            self.initial['end_time'] = self.instance.end_time.strftime('%H:%M')

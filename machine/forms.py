from django import forms
from attendance.models import Machine

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'ip_address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hapus autofocus default
        for field in self.fields.values():
            field.widget.attrs.pop('autofocus', None)

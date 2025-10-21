from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

class EmployeeEditForm(UserChangeForm):
    password = None  # hide password hash field

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "is_staff"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                # Checkbox pakai bootstrap form-check-input
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                # Input lain pakai form-control
                field.widget.attrs.update({"class": "form-control"})

from django.db import models
from employee.models import Employee

# Create your models here.
class Connect(models.TextChoices):
    NotConnected = "N", "Not-Connected"
    Connected = "Y", "Connected"


class Machine(models.Model):
    ip_address = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=1, choices=Connect.choices, default=Connect.NotConnected, null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Stores when the record is created
    updated_at = models.DateTimeField(
        auto_now=True
    )  # Updates when the record is modified

    def __str__(self) -> str:
        # Get all field names and values dynamically
        fields = [
            f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields
        ]
        return f"Machine({', '.join(fields)})"


class Attendance(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    user_id = models.CharField(max_length=20, default="")  # ID dari mesin
    timestamp = models.DateTimeField()
    verify_type = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('machine', 'user_id', 'timestamp')

    def __str__(self):
        return f"{self.user_id} - {self.timestamp}"

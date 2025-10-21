from django.db import models

# Create your models here.
class Dept(models.Model):
    id_dept = models.AutoField(primary_key=True)
    nama_dept = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
    # Get all field names and values dynamically
        fields = [f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields]
        return f"Dept({', '.join(fields)})"

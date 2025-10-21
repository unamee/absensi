from django.db import models

# Create your models here.
class Jabatan(models.Model):
    id_jabatan = models.AutoField(primary_key=True)
    kode_jabatan = models.CharField(max_length=10, default=None)
    nama_jabatan = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
    # Get all field names and values dynamically
        fields = [f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields]
        return f"Jabatan({', '.join(fields)})"

from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_karyawan = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    # def __str__(self) -> str:
    #     return f"{self.user.username} - {self.id_karyawan}"
    
    def __str__(self) -> str:
    # Get all field names and values dynamically
        fields = [f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields]
        return f"Employee({', '.join(fields)})"
    
    def save(self, *args, **kwargs):
        if self.id_karyawan and not self.qr_code:
            import qrcode
            from io import BytesIO
            from django.core.files import File

            qr = qrcode.make(self.id_karyawan)
            canvas = BytesIO()
            qr.save(canvas, format='PNG')
            qr_filename = f"qr_{self.id_karyawan}.png"
            self.qr_code.save(qr_filename, File(canvas), save=False)
            canvas.close()
        super().save(*args, **kwargs)

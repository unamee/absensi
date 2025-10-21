from django.db import models
from django.contrib.auth.models import User
import qrcode, os
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.core.exceptions import ValidationError


class Employee(models.Model):
    def validate_image(file):
        valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Only .jpg, .jpeg, .png, or .webp files are allowed.")

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_karyawan = models.CharField(max_length=10, unique=True)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    photo = models.ImageField(
        upload_to="employees/",
        default="employees/default.png",
        blank=True,
        null=True,
        validators=[validate_image],
    )

    # def __str__(self) -> str:
    #     return f"{self.user.username} - {self.id_karyawan}"

    def __str__(self) -> str:
        # Get all field names and values dynamically
        fields = [
            f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields
        ]
        return f"Employee({', '.join(fields)})"

    def save(self, *args, **kwargs):
        if self.id_karyawan and not self.qr_code:
            import qrcode
            from io import BytesIO
            from django.core.files import File

            qr = qrcode.make(self.id_karyawan)
            canvas = BytesIO()
            qr.save(canvas, format="PNG")
            qr_filename = f"qr_{self.id_karyawan}.png"
            self.qr_code.save(qr_filename, File(canvas), save=False)
            canvas.close()
        if not self.photo:
            self.photo = "employees/default.png"
        super().save(*args, **kwargs)

        # Auto resize foto jika bukan default.png
        if self.photo and self.photo.name != "employees/default.png":
            photo_path = self.photo.path
            try:
                img = Image.open(photo_path)

                # Resize ke 300x300 (square) sambil mempertahankan rasio
                img.thumbnail((300, 300))

                # Simpan ulang dalam format yang sama (JPEG/PNG)
                img.save(photo_path, quality=90, optimize=True)
            except Exception as e:
                print("⚠️ Error resizing image:", e)


class BreakLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    out_time = models.DateTimeField(default=timezone.now)
    in_time = models.DateTimeField(null=True, blank=True)

    @property
    def is_out(self):
        return self.in_time is None

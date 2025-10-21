from django.core.management.base import BaseCommand
from employee.models import Employee

class Command(BaseCommand):
    help = "Generate QR codes for all employees missing them"

    def handle(self, *args, **options):
        missing_qr = Employee.objects.filter(qr_code__isnull=True)
        count = missing_qr.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Semua employee sudah memiliki QR Code."))
            return

        for emp in missing_qr:
            emp.save()  # trigger auto-generate QR dari method save()
            self.stdout.write(f"🧾 Generated QR for {emp.id_karyawan} - {emp.user.username}")

        self.stdout.write(self.style.SUCCESS(f"🎉 Selesai! {count} QR Code berhasil dibuat."))

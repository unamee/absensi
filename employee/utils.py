import qrcode
from io import BytesIO
from django.core.files import File

def generate_qr_code(employee):
    """
    Membuat QR code baru untuk employee berdasarkan ID karyawan
    """
    qr_image = qrcode.make(employee.id_karyawan)
    qr_io = BytesIO()
    qr_image.save(qr_io, format="PNG")

    # Simpan ke model
    filename = f"qr_{employee.id_karyawan}.png"
    employee.qr_code.save(filename, File(qr_io), save=False)

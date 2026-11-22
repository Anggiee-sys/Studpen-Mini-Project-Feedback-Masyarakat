"""Membuat gambar QR code menuju halaman Beri Feedback.

Pakai (dari folder repo):
    pip install "qrcode[pil]"
    python buat_qr.py
Hasil: qr/qr_beri_feedback.png (dipakai di poster).
"""
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

URL = "https://feedback-kelurahan-geluran.streamlit.app/Beri_Feedback"
KELUARAN = Path("qr") / "qr_beri_feedback.png"

KELUARAN.parent.mkdir(exist_ok=True)
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=12, border=4)
qr.add_data(URL)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save(KELUARAN)
print("QR dibuat:", KELUARAN, "->", URL)

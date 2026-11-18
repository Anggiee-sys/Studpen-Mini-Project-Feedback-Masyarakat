"""Konfigurasi umum aplikasi: satu tempat untuk daftar layanan, aspek, dan kolom Sheet."""

NAMA_APP = "Feedback Pelayanan Kelurahan Geluran"

# Draf layanan (berdasarkan proposal). Verifikasi dengan pihak kelurahan sebelum dipakai sungguhan.
LAYANAN = [
    "Surat Keterangan",
    "SKTM (Surat Keterangan Tidak Mampu)",
    "Perubahan Data/Dokumen Kependudukan",
    "Konsultasi Warga",
    "Lainnya",
]

# Kolom di Sheet -> label yang tampil ke pengguna
ASPEK = {
    "Rating_Kecepatan": "Kecepatan pelayanan",
    "Rating_Sikap": "Sikap petugas",
    "Rating_Prosedur": "Kejelasan prosedur",
    "Rating_Informasi": "Kelengkapan informasi",
}

# Urutan kolom di Sheet (baris 1). HARUS sama persis dengan header di Google Sheets.
KOLOM = [
    "Timestamp",
    "Periode",
    "Layanan",
    *ASPEK.keys(),
    "Kritik_Saran",
    "Sumber_Data",
]

SUMBER_VALID = ("dummy", "uji_coba")
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

SUMBER_VALID = ("dummy", "uji_coba", "real")

# --- Tambahan Hari 2 ---
SUMBER_FORM = "uji_coba"   # nilai Sumber_Data untuk isian dari form selama masa uji coba
MAKS_KRITIK = 500          # batas karakter kritik/saran

# --- Tambahan Hari 4 (dashboard) ---
TAB_TINDAK_LANJUT = "tindak_lanjut"
KOLOM_TL = ["Timestamp", "Layanan", "Aspek", "Catatan", "Status"]
STATUS_TL = ["Direncanakan", "Dikerjakan", "Selesai"]
MAKS_CATATAN = 300

# DRAF indikator keberhasilan -- samakan angkanya dengan tabel indikator di proposal
TARGET_SKOR = 4.0          # target rata-rata skor kepuasan (skala 1-5)
TARGET_ISIAN_BULAN = 30    # target jumlah isian feedback per bulan

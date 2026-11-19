"""Validasi input form dan pemeriksaan kualitas data."""
import re

import pandas as pd

from config import ASPEK, KOLOM, LAYANAN, MAKS_KRITIK, SUMBER_VALID

# Pola data pribadi yang tidak boleh ada di kritik/saran (prinsip minimalisasi data, UU PDP)
POLA_DATA_PRIBADI = {
    "nomor identitas (16 digit)": re.compile(r"(?<!\d)\d{16}(?!\d)"),
    "nomor telepon": re.compile(r"(?<!\d)(?:\+62|62|0)8\d{8,11}(?!\d)"),
    "alamat email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
}


def deteksi_data_pribadi(teks: str) -> list:
    """Mengembalikan daftar jenis data pribadi yang terdeteksi di dalam teks."""
    teks = teks or ""
    # rapatkan angka yang dipisah spasi/titik/strip, mis. "0812-3456-7890" -> "081234567890"
    rapat = re.sub(r"(?<=\d)[\s.-]+(?=\d)", "", teks)
    return [nama for nama, pola in POLA_DATA_PRIBADI.items() if pola.search(rapat)]


def validasi_input(layanan, ratings: dict, kritik: str) -> list:
    """Memeriksa isian form. Mengembalikan daftar pesan kesalahan (kosong = valid)."""
    galat = []
    if layanan not in LAYANAN:
        galat.append("Pilih jenis layanan yang Anda terima.")
    for kolom, label in ASPEK.items():
        if ratings.get(kolom) not in (1, 2, 3, 4, 5):
            galat.append(f"Beri penilaian untuk aspek: {label}.")
    kritik = (kritik or "").strip()
    if len(kritik) > MAKS_KRITIK:
        galat.append(f"Kritik/saran maksimal {MAKS_KRITIK} karakter.")
    jenis = deteksi_data_pribadi(kritik)
    if jenis:
        galat.append(
            "Kritik/saran terdeteksi memuat " + ", ".join(jenis) + ". Mohon hapus data pribadi tersebut."
        )
    return galat


def cek_kualitas_data(df: pd.DataFrame) -> dict:
    """Memeriksa kualitas data feedback. Semua nilai 0 / daftar kosong berarti data bersih."""
    hasil = {"jumlah_baris": len(df)}
    hasil["kolom_hilang"] = [k for k in KOLOM if k not in df.columns]
    if hasil["kolom_hilang"]:
        return hasil

    wajib = [k for k in KOLOM if k != "Kritik_Saran"]  # kritik/saran memang opsional
    hasil["nilai_kosong"] = {
        k: int((df[k].isna() | df[k].astype(str).str.strip().isin(["", "nan"])).sum()) for k in wajib
    }
    hasil["baris_duplikat"] = int(df.duplicated().sum())

    di_luar_skala = {}
    for k in ASPEK:
        nilai = pd.to_numeric(df[k], errors="coerce")
        di_luar_skala[k] = int((nilai.notna() & ~nilai.between(1, 5)).sum())
    hasil["rating_di_luar_skala"] = di_luar_skala

    hasil["periode_tidak_valid"] = int((~df["Periode"].astype(str).str.match(r"^\d{4}-(0[1-9]|1[0-2])$")).sum())
    hasil["layanan_tidak_dikenal"] = int((~df["Layanan"].isin(LAYANAN)).sum())
    hasil["sumber_tidak_valid"] = int((~df["Sumber_Data"].isin(SUMBER_VALID)).sum())
    return hasil


def ringkas_kualitas(hasil: dict) -> str:
    """Mengubah hasil cek_kualitas_data menjadi teks ringkas untuk dibaca manusia."""
    if hasil.get("kolom_hilang"):
        return f"Kolom hilang: {hasil['kolom_hilang']}"
    masalah = []
    masalah += [f"kosong di {k}: {n}" for k, n in hasil["nilai_kosong"].items() if n]
    if hasil["baris_duplikat"]:
        masalah.append(f"baris duplikat: {hasil['baris_duplikat']}")
    masalah += [f"rating di luar 1-5 di {k}: {n}" for k, n in hasil["rating_di_luar_skala"].items() if n]
    for nama in ("periode_tidak_valid", "layanan_tidak_dikenal", "sumber_tidak_valid"):
        if hasil[nama]:
            masalah.append(f"{nama.replace('_', ' ')}: {hasil[nama]}")
    if not masalah:
        return f"Data bersih: {hasil['jumlah_baris']} baris, tidak ada masalah ditemukan."
    return f"{hasil['jumlah_baris']} baris. Masalah: " + "; ".join(masalah)
"""Kategorisasi kritik/saran berbasis aturan kata kunci (rule-based, bukan AI).

Satu teks bisa masuk lebih dari satu kategori. Teks yang tidak cocok kata kunci apa pun
masuk "Lainnya". Pendekatan AI/ABSA direncanakan pada pengembangan lanjutan (Tugas Akhir).
"""
import re

import pandas as pd

KATEGORI = {
    "Kecepatan/Antrean": ["antre", "antri", "lama", "menunggu", "nunggu", "cepat", "lambat", "loket", "waktu", "estimasi", "selesai"],
    "Sikap Petugas": ["ramah", "judes", "sabar", "sopan", "petugas", "galak", "cuek", "terburu"],
    "Prosedur/Persyaratan": ["prosedur", "alur", "syarat", "persyaratan", "berkas", "bingung", "bolak-balik", "urutan", "dokumen"],
    "Informasi": ["informasi", "info", "pengumuman", "brosur", "papan", "jam layanan", "sosialisasi", "penjelasan"],
    "Biaya": ["biaya", "bayar", "tarif", "pungli", "pungutan", "uang", "gratis", "mahal", "administrasi"],
    "Sarana/Prasarana": ["ruang tunggu", "kursi", "parkir", "ac ", "toilet", "sempit", "panas", "fasilitas", "sarana"],
}
KATA_POSITIF = ["terima kasih", "baik", "puas", "bagus", "lancar", "dipertahankan", "membantu", "mudah dipahami"]
KATA_NEGASI = ["tidak", "kurang", "belum", "sulit", "tak ", "bukan"]


def _bersih(teks) -> str:
    if teks is None or (not isinstance(teks, str) and pd.isna(teks)):
        teks = ""
    return re.sub(r"\s+", " ", str(teks or "").lower()).strip() + " "


def kategorikan_teks(teks) -> list:
    """Daftar kategori untuk satu teks. Teks kosong -> []."""
    t = _bersih(teks)
    if not t.strip():
        return []
    hasil = [k for k, kata in KATEGORI.items() if any(w in t for w in kata)]
    if not hasil:
        hasil = ["Apresiasi"] if any(w in t for w in KATA_POSITIF) else ["Lainnya"]
    return hasil


def nada_teks(teks) -> str:
    """Nada sederhana: 'positif', 'negatif', atau 'netral' (kasar, hanya kata kunci)."""
    t = _bersih(teks)
    if not t.strip():
        return "kosong"
    neg = any(w in t for w in KATA_NEGASI) or any(w in t for w in ["lama", "judes", "bingung", "sempit", "panas", "antre", "antri", "terburu"])
    pos = any(w in t for w in KATA_POSITIF)
    if neg:
        return "negatif"
    return "positif" if pos else "netral"


def tambah_kategori(df: pd.DataFrame) -> pd.DataFrame:
    """Menambah kolom Kategori (daftar) dan Nada ke DataFrame."""
    d = df.copy()
    d["Kategori"] = d["Kritik_Saran"].apply(kategorikan_teks)
    d["Nada"] = d["Kritik_Saran"].apply(nada_teks)
    return d


def hitung_kategori(df: pd.DataFrame) -> pd.DataFrame:
    """Jumlah teks per kategori (hanya baris yang ada teksnya)."""
    d = df if "Kategori" in df else tambah_kategori(df)
    d = d[d["Kategori"].str.len() > 0]
    jumlah = d.explode("Kategori")["Kategori"].value_counts()
    return jumlah.rename_axis("Kategori").reset_index(name="Jumlah")


def contoh_teks(df: pd.DataFrame, kategori: str, maks: int = 3) -> list:
    d = df if "Kategori" in df else tambah_kategori(df)
    cocok = d[d["Kategori"].apply(lambda k: kategori in k)]
    return cocok["Kritik_Saran"].drop_duplicates().head(maks).tolist()

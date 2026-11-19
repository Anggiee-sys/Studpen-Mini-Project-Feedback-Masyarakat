"""Modul analisis statistik feedback.

Murni pandas (tanpa Streamlit), jadi bisa dipakai di notebook Colab maupun di aplikasi.
"""
import numpy as np
import pandas as pd

from config import ASPEK

AMBANG_N_KECIL = 30        # di bawah ini, hasil dianggap kurang stabil
AMBANG_SKOR_RENDAH = 3.5   # rata-rata di bawah ini ditandai "perlu perhatian"
AMBANG_PENURUNAN = 0.3     # penurunan rata-rata antarperiode yang ditandai
N_MIN_PERIODE = 10         # n minimal per periode agar perbandingan dianggap layak

KOLOM_ASPEK = list(ASPEK)


def siapkan(df: pd.DataFrame, sumber=None) -> pd.DataFrame:
    """Menyiapkan data: rating dijadikan angka, baris tidak valid dibuang, opsional filter Sumber_Data.

    sumber: None (semua), satu nilai (mis. "dummy"), atau daftar nilai (mis. ["uji_coba", "real"]).
    """
    d = df.copy()
    for k in KOLOM_ASPEK:
        d[k] = pd.to_numeric(d[k], errors="coerce")
    d = d.dropna(subset=KOLOM_ASPEK)
    d = d[d[KOLOM_ASPEK].apply(lambda s: s.between(1, 5)).all(axis=1)]
    if sumber is not None:
        pilihan = [sumber] if isinstance(sumber, str) else list(sumber)
        d = d[d["Sumber_Data"].isin(pilihan)]
    d = d.assign(Skor_Rata=d[KOLOM_ASPEK].mean(axis=1))
    return d.reset_index(drop=True)


def ringkasan_umum(df: pd.DataFrame) -> dict:
    """Angka ringkas untuk kartu KPI."""
    n = len(df)
    return {
        "jumlah_responden": n,
        "skor_rata_rata": round(float(df["Skor_Rata"].mean()), 2) if n else None,
        "jumlah_layanan": int(df["Layanan"].nunique()),
        "jumlah_periode": int(df["Periode"].nunique()),
        "n_kecil": n < AMBANG_N_KECIL,
    }


def statistik_per_aspek(df: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata, median, simpangan baku, skewness, dan selang kepercayaan 95% tiap aspek."""
    baris = []
    for kolom, label in ASPEK.items():
        x = df[kolom]
        n = int(x.count())
        rata = x.mean()
        sd = x.std(ddof=1) if n > 1 else np.nan
        se = sd / np.sqrt(n) if n > 1 else np.nan
        baris.append(
            {
                "Kolom": kolom,
                "Aspek": label,
                "n": n,
                "Rata-rata": rata,
                "Median": x.median(),
                "Std": sd,
                "Skewness": x.skew(),
                "CI95 bawah": rata - 1.96 * se,
                "CI95 atas": rata + 1.96 * se,
            }
        )
    return pd.DataFrame(baris).round(2)


def distribusi_rating(df: pd.DataFrame, persen: bool = True) -> pd.DataFrame:
    """Sebaran rating 1-5 per aspek (baris = aspek, kolom = nilai rating)."""
    hasil = {}
    for kolom, label in ASPEK.items():
        hitung = df[kolom].value_counts().reindex(range(1, 6), fill_value=0)
        if persen and hitung.sum() > 0:
            hitung = (hitung / hitung.sum() * 100).round(1)
        hasil[label] = hitung
    return pd.DataFrame(hasil).T.rename_axis("Aspek")


def skor_per_layanan(df: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata tiap aspek per jenis layanan, diurutkan dari skor terendah."""
    g = df.groupby("Layanan")
    t = g[KOLOM_ASPEK].mean().round(2).rename(columns=ASPEK)
    t["Skor rata-rata"] = g["Skor_Rata"].mean().round(2)
    t["n"] = g.size()
    return t.sort_values("Skor rata-rata")


def tren_periode(df: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata tiap aspek per periode (bulan)."""
    g = df.groupby("Periode")
    t = g[KOLOM_ASPEK].mean().round(2).rename(columns=ASPEK)
    t["Skor rata-rata"] = g["Skor_Rata"].mean().round(2)
    t["n"] = g.size()
    return t.sort_index()


def perubahan_periode(df: pd.DataFrame):
    """Membandingkan periode terakhir dengan periode sebelumnya. None bila periode < 2."""
    t = tren_periode(df)
    if len(t) < 2:
        return None
    sebelum, akhir = t.iloc[-2], t.iloc[-1]
    tabel = pd.DataFrame(
        {
            "Aspek": list(ASPEK.values()),
            "Sebelumnya": [sebelum[a] for a in ASPEK.values()],
            "Terakhir": [akhir[a] for a in ASPEK.values()],
        }
    )
    tabel["Selisih"] = (tabel["Terakhir"] - tabel["Sebelumnya"]).round(2)
    return {
        "periode_sebelum": t.index[-2],
        "periode_akhir": t.index[-1],
        "n_sebelum": int(sebelum["n"]),
        "n_akhir": int(akhir["n"]),
        "layak": int(sebelum["n"]) >= N_MIN_PERIODE and int(akhir["n"]) >= N_MIN_PERIODE,
        "tabel": tabel,
    }


def daftar_perhatian(df: pd.DataFrame) -> list:
    """Aspek yang perlu perhatian: skor rendah, atau turun tajam dibanding periode sebelumnya."""
    hasil = []
    stat = statistik_per_aspek(df)
    for _, r in stat.iterrows():
        if r["Rata-rata"] < AMBANG_SKOR_RENDAH:
            hasil.append(
                {"aspek": r["Aspek"], "jenis": "skor rendah", "nilai": r["Rata-rata"],
                 "keterangan": f"rata-rata {r['Rata-rata']:.2f} (di bawah {AMBANG_SKOR_RENDAH})"}
            )
    banding = perubahan_periode(df)
    if banding and banding["layak"]:
        for _, r in banding["tabel"].iterrows():
            if r["Selisih"] <= -AMBANG_PENURUNAN:
                hasil.append(
                    {"aspek": r["Aspek"], "jenis": "penurunan", "nilai": r["Selisih"],
                     "keterangan": f"turun {abs(r['Selisih']):.2f} dari {banding['periode_sebelum']} ke {banding['periode_akhir']}"}
                )
    return hasil


def tren_layanan(df: pd.DataFrame, kolom_aspek: str = "Rating_Kecepatan") -> pd.DataFrame:
    """Rata-rata satu aspek per layanan per periode (baris = periode, kolom = layanan) plus n tiap sel."""
    rata = df.pivot_table(index="Periode", columns="Layanan", values=kolom_aspek, aggfunc="mean").round(2)
    return rata.sort_index()


def jumlah_per_layanan_periode(df: pd.DataFrame) -> pd.DataFrame:
    """Jumlah isian per layanan per periode (untuk memeriksa apakah tiap kelompok cukup besar)."""
    return df.pivot_table(index="Periode", columns="Layanan", values="Skor_Rata", aggfunc="size", fill_value=0)

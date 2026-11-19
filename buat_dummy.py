"""Generator data DUMMY (simulasi) feedback Kelurahan Geluran.

Semua data di sini SIMULASI, bukan feedback warga sungguhan. Polanya sengaja dibuat
agar dashboard bisa didemokan (misalnya antrean SKTM yang membaik, prosedur perubahan
data yang selalu rendah).

Cara pakai (dari folder repo):
    python buat_dummy.py             -> hanya membuat data/dummy_feedback.csv
    python buat_dummy.py --unggah    -> membuat CSV lalu mengunggahnya ke Google Sheets
                                        (hanya jika tab 'feedback' masih kosong)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from config import ASPEK, KOLOM, LAYANAN
from validasi import cek_kualitas_data, ringkas_kualitas

SEED = 2026
KELUARAN = Path("data") / "dummy_feedback.csv"

# Lokasi kunci JSON (sama seperti buat_secrets.py) -- hanya dipakai saat --unggah
BASE = Path.home() / "Downloads" / "Gita-Project"
KEYS_DIR = BASE / "Keys-Rahasia-Feedback-Masyarakat"
NAMA_SHEET = "Mini-Project-Feedback-Masyarakat"
NAMA_TAB = "feedback"

L_SK, L_SKTM, L_DATA, L_KONSUL, L_LAIN = LAYANAN

# Jumlah baris dan rentang hari kerja per periode
PERIODE = {
    "2026-08": (85, "2026-08-10", "2026-08-31"),
    "2026-09": (70, "2026-09-01", "2026-09-30"),
    "2026-10": (75, "2026-10-01", "2026-10-30"),
    "2026-11": (60, "2026-11-02", "2026-11-17"),
}
LIBUR = {"2026-08-17"}

# Proporsi layanan per periode (SKTM ramai di Agustus karena tahun ajaran baru)
PROPORSI = {
    "2026-08": [0.26, 0.30, 0.22, 0.15, 0.07],
    "2026-09": [0.32, 0.20, 0.26, 0.15, 0.07],
    "2026-10": [0.32, 0.18, 0.28, 0.15, 0.07],
    "2026-11": [0.30, 0.18, 0.30, 0.16, 0.06],
}

# Rata-rata dasar: (kecepatan, sikap, prosedur, informasi)
RATA_DASAR = {
    L_SK: (3.9, 4.3, 3.8, 3.7),
    L_SKTM: (3.3, 4.2, 3.4, 3.5),
    L_DATA: (3.5, 4.1, 2.9, 3.3),
    L_KONSUL: (4.2, 4.4, 4.0, 3.9),
    L_LAIN: (3.8, 4.2, 3.7, 3.6),
}
URUTAN_ASPEK = list(ASPEK.keys())

# Penyesuaian per (periode, layanan, aspek). Layanan None = semua layanan.
PENYESUAIAN = {
    ("2026-08", L_SKTM, "Rating_Kecepatan"): -0.8,
    ("2026-09", L_SKTM, "Rating_Kecepatan"): -0.1,
    ("2026-10", L_SKTM, "Rating_Kecepatan"): +0.2,
    ("2026-11", L_SKTM, "Rating_Kecepatan"): +0.4,
    ("2026-11", L_DATA, "Rating_Kecepatan"): -0.8,
    ("2026-08", None, "Rating_Informasi"): -0.3,
    ("2026-10", None, "Rating_Informasi"): +0.1,
    ("2026-11", None, "Rating_Informasi"): +0.2,
}

TEKS_NEGATIF = {
    "Rating_Kecepatan": [
        "Antrean panjang sekali, menunggu hampir dua jam.",
        "Prosesnya lama, surat baru selesai besok padahal butuh cepat.",
        "Mohon ditambah loket, antrian terlalu lama saat jam sibuk.",
        "Menunggu lama untuk SKTM, apalagi menjelang masuk sekolah.",
        "Waktu pengerjaan tidak sesuai perkiraan petugas.",
        "Antri dari pagi baru dilayani siang.",
    ],
    "Rating_Sikap": [
        "Petugas kurang ramah saat saya bertanya.",
        "Penjelasan petugas terkesan terburu-buru.",
        "Petugas kurang sabar menjelaskan.",
        "Ada petugas yang judes, mohon lebih ramah ke warga.",
    ],
    "Rating_Prosedur": [
        "Persyaratan berkasnya membingungkan, saya bolak-balik karena ada yang kurang.",
        "Alur pengurusan tidak jelas, harus mulai dari mana.",
        "Prosedur perubahan data kurang dijelaskan, saya harus datang dua kali.",
        "Syarat berkas berubah-ubah, mohon dijelaskan sejak awal.",
        "Bingung urutan loket yang harus didatangi.",
    ],
    "Rating_Informasi": [
        "Informasi persyaratan tidak ada di papan pengumuman.",
        "Sulit mencari info jam layanan dan biaya.",
        "Mohon dibuatkan brosur atau informasi yang lebih jelas.",
        "Tidak ada info estimasi waktu penyelesaian.",
    ],
}
TEKS_SARANA = [
    "Ruang tunggu sempit dan kursinya kurang.",
    "Parkir penuh dan panas di ruang tunggu.",
    "AC di ruang tunggu tidak dingin.",
]
TEKS_POSITIF = [
    "Pelayanan sudah baik, terima kasih.",
    "Petugas ramah dan membantu.",
    "Prosesnya cepat dan jelas, puas.",
    "Sudah bagus, tolong dipertahankan.",
    "Terima kasih, urusan selesai dengan lancar.",
    "Penjelasan petugas mudah dipahami.",
    "Pelayanan cepat, tidak perlu menunggu lama.",
]


def _pilih_kritik(rng, rating: dict) -> str:
    nilai = [rating[k] for k in URUTAN_ASPEK]
    terendah = min(nilai)
    if terendah <= 2:
        peluang_isi = 0.85
    elif terendah == 3:
        peluang_isi = 0.5
    else:
        peluang_isi = 0.4
    if rng.random() > peluang_isi:
        return ""
    if terendah >= 4:
        return str(rng.choice(TEKS_POSITIF))
    if rng.random() < 0.08:
        return str(rng.choice(TEKS_SARANA))
    kandidat = [k for k in URUTAN_ASPEK if rating[k] == terendah]
    aspek = str(rng.choice(kandidat))
    return str(rng.choice(TEKS_NEGATIF[aspek]))


def buat_dummy() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    baris = []
    for periode, (jumlah, awal, akhir) in PERIODE.items():
        hari = [d for d in pd.bdate_range(awal, akhir) if d.strftime("%Y-%m-%d") not in LIBUR]
        # jumlah per layanan dibuat pasti (bukan acak) supaya tiap kelompok cukup besar
        banyak = np.round(np.array(PROPORSI[periode]) * jumlah).astype(int)
        banyak[0] += jumlah - banyak.sum()  # koreksi pembulatan
        layanan_terpilih = rng.permutation(np.repeat(LAYANAN, banyak))
        for layanan in layanan_terpilih:
            tanggal = hari[rng.integers(len(hari))]
            waktu = tanggal + pd.Timedelta(
                hours=int(rng.integers(8, 15)),
                minutes=int(rng.integers(0, 60)),
                seconds=int(rng.integers(0, 60)),
            )
            suasana = rng.normal(0, 0.5)  # "mood" umum responden agar antaraspek saling berkaitan
            rating = {}
            for kolom, dasar in zip(URUTAN_ASPEK, RATA_DASAR[layanan]):
                rata = dasar + suasana + PENYESUAIAN.get((periode, None, kolom), 0)
                rata += PENYESUAIAN.get((periode, layanan, kolom), 0)
                rating[kolom] = int(np.clip(round(rng.normal(rata, 0.6)), 1, 5))
            baris.append(
                {
                    "Timestamp": waktu.strftime("%Y-%m-%d %H:%M:%S"),
                    "Periode": periode,
                    "Layanan": layanan,
                    **rating,
                    "Kritik_Saran": _pilih_kritik(rng, rating),
                    "Sumber_Data": "dummy",
                }
            )
    df = pd.DataFrame(baris, columns=KOLOM).sort_values("Timestamp").reset_index(drop=True)
    return df


def unggah(df: pd.DataFrame) -> None:
    import gspread

    kunci = list(KEYS_DIR.glob("*.json"))
    if len(kunci) != 1:
        raise SystemExit(f"Harus ada tepat 1 file .json di {KEYS_DIR}, ditemukan: {len(kunci)}")
    klien = gspread.service_account(filename=str(kunci[0]))
    ws = klien.open(NAMA_SHEET).worksheet(NAMA_TAB)

    isi = ws.get_all_values()
    if not isi or isi[0] != KOLOM:
        raise SystemExit(f"Header di Sheet tidak sesuai skema.\nSeharusnya: {KOLOM}\nDi Sheet   : {isi[0] if isi else []}")
    if len(isi) > 1:
        raise SystemExit(
            f"Tab '{NAMA_TAB}' sudah berisi {len(isi) - 1} baris data. Pengunggahan dibatalkan agar tidak dobel.\n"
            "Kosongkan baris 2 ke bawah di Sheet jika ingin mengunggah ulang."
        )
    nilai = [[r[k] for k in KOLOM] for r in df.to_dict("records")]
    ws.append_rows(nilai, value_input_option="RAW")
    print(f"Berhasil mengunggah {len(nilai)} baris ke tab '{NAMA_TAB}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--unggah", action="store_true", help="unggah ke Google Sheets")
    args = parser.parse_args()

    data = buat_dummy()
    KELUARAN.parent.mkdir(exist_ok=True)
    data.to_csv(KELUARAN, index=False, encoding="utf-8")
    print(f"CSV dibuat: {KELUARAN} ({len(data)} baris)")
    print("Pemeriksaan kualitas:", ringkas_kualitas(cek_kualitas_data(data)))
    print("\nRata-rata rating per periode:")
    print(data.groupby("Periode")[URUTAN_ASPEK].mean().round(2))
    if args.unggah:
        unggah(data)
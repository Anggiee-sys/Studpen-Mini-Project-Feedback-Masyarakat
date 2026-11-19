"""Pembuat insight otomatis (Temuan - Insight - Rekomendasi) berbasis aturan, bukan AI."""
import analisis as a
import teks as t

# Rekomendasi standar per aspek (bahasa sederhana, perlu dikonfirmasi pihak kelurahan)
REKOMENDASI_ASPEK = {
    "Kecepatan pelayanan": "Tinjau alur antrean dan beban loket pada jam sibuk; pertimbangkan estimasi waktu penyelesaian yang dipasang terbuka.",
    "Sikap petugas": "Ingatkan standar keramahan dan komunikasi melalui briefing singkat petugas.",
    "Kejelasan prosedur": "Sederhanakan dan tampilkan alur serta persyaratan layanan secara jelas (poster/brosur) sebelum warga ke loket.",
    "Kelengkapan informasi": "Lengkapi informasi persyaratan, biaya, dan jam layanan di papan pengumuman dan media kelurahan.",
}


def buat_insight(df) -> list:
    """df: hasil analisis.siapkan(). Mengembalikan daftar dict {temuan, insight, rekomendasi}."""
    hasil = []
    n = len(df)
    if n < a.AMBANG_N_KECIL:
        hasil.append({"temuan": f"Jumlah isian baru {n}.", "insight": "Hasil belum stabil untuk disimpulkan.",
                      "rekomendasi": "Kumpulkan lebih banyak isian sebelum mengambil keputusan."})
        return hasil

    for x in a.daftar_perhatian(df):
        if x["jenis"] == "skor rendah":
            hasil.append({"temuan": f"{x['aspek']}: {x['keterangan']}.",
                          "insight": f"Aspek ini termasuk yang paling rendah dinilai warga.",
                          "rekomendasi": REKOMENDASI_ASPEK[x["aspek"]]})
        else:
            hasil.append({"temuan": f"{x['aspek']}: {x['keterangan']}.",
                          "insight": "Penurunan antarperiode perlu dicermati; periksa apakah ada perubahan alur atau lonjakan layanan.",
                          "rekomendasi": REKOMENDASI_ASPEK[x["aspek"]]})

    # layanan terendah
    sl = a.skor_per_layanan(df)
    besar = sl[sl["n"] >= a.N_MIN_PERIODE]
    if len(besar):
        nama, baris = besar.index[0], besar.iloc[0]
        aspek_rendah = baris[[v for v in a.ASPEK.values()]].astype(float).idxmin()
        hasil.append({"temuan": f"Layanan dengan skor terendah: {nama} ({baris['Skor rata-rata']:.2f}, n={int(baris['n'])}); aspek terlemah: {aspek_rendah}.",
                      "insight": "Layanan ini menjadi kandidat prioritas perbaikan.",
                      "rekomendasi": REKOMENDASI_ASPEK[aspek_rendah]})

    # kategori teks terbanyak (hanya teks bernada negatif)
    dk = t.tambah_kategori(df)
    neg = dk[dk["Nada"] == "negatif"]
    if len(neg) >= 5:
        top = t.hitung_kategori(neg).iloc[0]
        hasil.append({"temuan": f"Keluhan tertulis paling sering menyangkut '{top['Kategori']}' ({int(top['Jumlah'])} dari {len(neg)} teks bernada negatif).",
                      "insight": "Kategori ini paling banyak muncul pada keluhan tertulis; bandingkan dengan skor rating aspek terkait.",
                      "rekomendasi": "Prioritaskan perbaikan pada kategori ini, lalu pantau perubahannya bulan berikutnya."})
    return hasil

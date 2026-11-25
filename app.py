import streamlit as st

import analisis as a
import sheets
from config import LAYANAN, NAMA_APP

st.set_page_config(page_title=NAMA_APP, page_icon="🏛️", layout="centered")

st.title(NAMA_APP)
st.caption("Prototipe Studi Independen UNESA × Celerates")

st.write(
    "Bantu kelurahan meningkatkan pelayanan: beri penilaian atas layanan yang Anda terima. "
    "Cukup 1 menit dan **tanpa nama**."
)
st.page_link("pages/1_Beri_Feedback.py", label="Beri Feedback", icon="📝")

st.header("Informasi Pelayanan")
st.markdown(
    "**Jam buka:** 08.00-16.00 | **Jam layanan:** 09.00-15.00 | **Lama layanan:** sekitar 15-20 menit"
)
st.markdown(
    "| Layanan | Gambaran persyaratan |\n"
    "|---|---|\n"
    "| Surat Keterangan (umum, usaha, ahli waris) | Pengantar RT/RW, fotokopi KK dan KTP pemohon, surat pernyataan bermaterai; "
    "tambahan sesuai jenis (misalnya dokumen usaha atau akta kematian dan KTP ahli waris) |\n"
    "| SKTM | Pengantar RT/RW, fotokopi KK dan KTP pemohon, surat dari puskesmas/rawat inap (untuk rumah sakit), surat pernyataan bermaterai |\n"
    "| Perubahan Data/Dokumen Kependudukan | Akta kelahiran/kematian: KK, KTP, surat keterangan bidan/dokter/kelurahan, KTP saksi. "
    "Pindah masuk/keluar: KK, KTP, surat pindah/domisili, surat pernyataan alamat atau kepemilikan rumah |\n"
    "| Konsultasi Warga | Sampaikan keperluan langsung kepada petugas |\n"
)
with st.expander("Alur layanan secara singkat"):
    st.markdown(
        "1. Pemohon menyerahkan dokumen sesuai persyaratan, petugas memverifikasi.\n"
        "2. Petugas memproses pengajuan (membuat akun dan pengajuan, mengisi uraian layanan).\n"
        "3. Petugas memverifikasi dokumen kepada atasan.\n"
        "4. Atasan memverifikasi dokumen dan menandatangani."
    )
st.caption(
    "Ringkasan umum untuk gambaran awal, bersumber dari keterangan perangkat kelurahan. Persyaratan lengkap dan terbaru "
    "ada pada poster di kelurahan; bawa dokumen asli untuk diverifikasi petugas."
)

# ---------- Ringkasan terbuka (transparansi): hanya dari data SUNGGUHAN, hanya angka rangkuman ----------
st.header("Ringkasan Penilaian Warga")
try:
    real = a.siapkan(sheets.muat_data(), sumber="real")
except Exception:
    real = None
    st.caption("Ringkasan belum dapat dimuat saat ini.")
if real is not None:
    if len(real) < a.AMBANG_N_KECIL:
        st.caption(
            f"Ringkasan akan ditampilkan setelah terkumpul sedikitnya {a.AMBANG_N_KECIL} penilaian warga. "
            f"Saat ini baru {len(real)}."
        )
    else:
        r = a.ringkasan_umum(real)
        c1, c2 = st.columns(2)
        c1.metric("Jumlah penilaian", r["jumlah_responden"])
        c2.metric("Skor rata-rata (1-5)", r["skor_rata_rata"])
        st.dataframe(
            a.statistik_per_aspek(real)[["Aspek", "Rata-rata"]], hide_index=True, width="stretch"
        )
        st.caption("Hanya angka rangkuman; tidak memuat identitas maupun kritik/saran individual.")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.page_link("pages/2_Dashboard.py", label="Dashboard (operator/pimpinan)", icon="📊")
with c2:
    st.page_link("pages/3_Tentang.py", label="Tentang aplikasi", icon="ℹ️")

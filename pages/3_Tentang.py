import streamlit as st

from config import ASPEK, NAMA_APP

st.set_page_config(page_title="Tentang", page_icon="ℹ️", layout="centered")

st.title("Tentang Aplikasi")
st.write(
    f"**{NAMA_APP}** adalah prototipe sistem informasi dan monitoring kualitas pelayanan publik "
    "berbasis feedback masyarakat. Prototipe ini disusun dalam program Studi Independen "
    "(UNESA × Celerates) dengan Kelurahan Geluran, Kecamatan Taman, Kabupaten Sidoarjo, sebagai mitra implementasi."
)

st.header("Cara kerja")
st.markdown(
    "1. Warga mengisi penilaian layanan melalui formulir (tanpa nama).\n"
    "2. Data tersimpan di Google Sheets.\n"
    "3. Operator dan pimpinan kelurahan melihat ringkasan, tren, dan insight di dashboard.\n"
    "4. Hasil dipakai sebagai bahan perbaikan pelayanan dan dicatat sebagai tindak lanjut."
)

st.header("Informasi layanan Kelurahan Geluran")
st.markdown(
    "- **Jam buka:** 08.00-16.00. **Jam layanan:** 09.00-15.00.\n"
    "- **Lama layanan:** sekitar 15-20 menit.\n"
    "- **Layanan yang sering diakses:** Surat Keterangan (umum, usaha, ahli waris), SKTM, dan "
    "dokumen kependudukan (akta kelahiran, akta kematian, pindah masuk, pindah keluar).\n"
    "- **Persyaratan lengkap tiap layanan:** lihat poster persyaratan di kelurahan."
)
st.markdown("**Alur layanan secara singkat**")
st.markdown(
    "1. Pemohon menyerahkan dokumen sesuai persyaratan, petugas memverifikasi.\n"
    "2. Petugas memproses pengajuan (membuat akun dan pengajuan, mengisi uraian layanan).\n"
    "3. Petugas memverifikasi dokumen kepada atasan.\n"
    "4. Atasan memverifikasi dokumen dan menandatangani."
)
st.caption("Informasi bersumber dari keterangan perangkat kelurahan dan merupakan fitur pendukung, bukan inti sistem.")

st.header("Aspek yang dinilai")
for label in ASPEK.values():
    st.markdown(f"- {label}")
st.caption(
    "Aspek penilaian mengacu pada unsur Survei Kepuasan Masyarakat (PermenPAN-RB No. 14 Tahun 2017). "
    "Unsur lain, seperti biaya dan sarana, ditangkap melalui kritik/saran tertulis."
)

st.header("Data dan privasi")
st.markdown(
    "- Formulir **tidak meminta nama, NIK, alamat, atau nomor telepon**. Isian yang memuat data semacam itu ditolak.\n"
    "- Yang disimpan: jenis layanan, empat penilaian (1-5), kritik/saran opsional, waktu, dan sumber data.\n"
    "- Penilaian warga hanya dapat dilihat dalam bentuk rangkuman angka oleh publik; "
    "kritik/saran individual hanya dilihat operator kelurahan.\n"
    "- Sumber data ditandai **real** (warga sungguhan), **uji_coba** (pengujian), atau **dummy** (simulasi). "
    "Ringkasan publik di beranda hanya memakai data *real*.\n"
    "- Lama penyimpanan data akan disepakati bersama pihak kelurahan."
)

st.header("Kontribusi pada tujuan pembangunan berkelanjutan (SDGs)")
st.caption("Kontribusi bersifat mendukung pada skala prototipe, bukan klaim dampak yang sudah terukur.")
st.table(
    {
        "SDG": [
            "16 Perdamaian, keadilan, dan kelembagaan yang tangguh (utama)",
            "1 Tanpa kemiskinan (pendukung)",
            "4 Pendidikan berkualitas (pendukung)",
            "17 Kemitraan untuk mencapai tujuan (pendukung)",
        ],
        "Bentuk dukungan": [
            "Mendukung institusi yang lebih akuntabel dan transparan (target 16.6) dan pengambilan "
            "keputusan yang responsif dengan partisipasi warga (target 16.7) melalui kanal feedback dan monitoring layanan.",
            "Memantau kualitas layanan yang dekat dengan warga kurang mampu, seperti SKTM, sehingga hambatan layanan lebih mudah terlihat.",
            "SKTM sering dibutuhkan saat masa kenaikan sekolah; pemantauan layanan ini berpotensi membantu kelancaran akses administrasi pendidikan (dukungan tidak langsung).",
            "Kerja sama perguruan tinggi, mitra program, dan kelurahan dalam mengembangkan dan mencoba solusi (target 17.17).",
        ],
    }
)

st.page_link("app.py", label="Kembali ke beranda", icon="🏠")

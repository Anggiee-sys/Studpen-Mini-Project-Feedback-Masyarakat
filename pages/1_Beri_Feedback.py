import time
from datetime import datetime, timedelta, timezone

import streamlit as st

import sheets
from config import ASPEK, LAYANAN, MAKS_KRITIK, SUMBER_FORM
from validasi import validasi_input

WIB = timezone(timedelta(hours=7))
JEDA_DETIK = 20  # jeda minimal antar pengiriman dari satu sesi (pencegah kirim ganda)

st.set_page_config(page_title="Beri Feedback", page_icon="📝", layout="centered")

st.title("Beri Feedback")
st.write("Ceritakan pengalaman Anda dilayani di Kelurahan Geluran. Cukup 1 menit dan **tanpa nama**.")

with st.expander("Privasi data Anda"):
    st.markdown(
        "- Kami **tidak** meminta nama atau identitas Anda.\n"
        "- Data yang disimpan: jenis layanan, penilaian, dan kritik/saran.\n"
        "- Data dipakai untuk mengevaluasi dan meningkatkan pelayanan kelurahan. "
        "Hasil yang ditampilkan ke publik hanya berupa angka rangkuman.\n"
        "- **Jangan menulis data pribadi** (nama, NIK, alamat, nomor HP) pada kritik/saran."
    )

# Tampilan setelah berhasil mengirim
if st.session_state.get("terkirim"):
    st.success("Terima kasih! Feedback Anda sudah terkirim.")
    if st.button("Kirim feedback lagi"):
        for kunci in (*ASPEK.keys(), "f_layanan", "f_kritik"):  # kosongkan isian sebelumnya
            st.session_state.pop(kunci, None)
        st.session_state["terkirim"] = False
        st.rerun()
    st.stop()

with st.form("form_feedback"):
    layanan = st.selectbox(
        "Layanan yang Anda terima", LAYANAN, index=None, placeholder="Pilih layanan...", key="f_layanan"
    )
    st.caption("Beri penilaian untuk tiap aspek: 1 = sangat buruk, 5 = sangat baik")
    ratings = {}
    for kolom, label in ASPEK.items():
        ratings[kolom] = st.radio(label, [1, 2, 3, 4, 5], index=None, horizontal=True, key=kolom)
    kritik = st.text_area(
        "Kritik dan saran (opsional)",
        max_chars=MAKS_KRITIK,
        key="f_kritik",
        placeholder="Tuliskan pengalaman atau saran Anda untuk perbaikan layanan.",
    )
    kirim = st.form_submit_button("Kirim Feedback", type="primary")

if kirim:
    galat = validasi_input(layanan, ratings, kritik)
    sekarang = time.time()
    if sekarang - st.session_state.get("terakhir_kirim", 0) < JEDA_DETIK:
        galat.append("Mohon tunggu sebentar sebelum mengirim lagi.")

    if galat:
        for pesan in galat:
            st.error(pesan)
    else:
        waktu = datetime.now(WIB)
        baris = {
            "Timestamp": waktu.strftime("%Y-%m-%d %H:%M:%S"),
            "Periode": waktu.strftime("%Y-%m"),
            "Layanan": layanan,
            **ratings,
            "Kritik_Saran": (kritik or "").strip(),
            "Sumber_Data": SUMBER_FORM,
        }
        try:
            sheets.tambah_feedback(baris)
        except Exception:
            st.error("Maaf, feedback belum berhasil terkirim. Silakan coba lagi beberapa saat lagi.")
        else:
            st.session_state["terkirim"] = True
            st.session_state["terakhir_kirim"] = sekarang
            st.rerun()

st.page_link("app.py", label="Kembali ke beranda", icon="🏠")
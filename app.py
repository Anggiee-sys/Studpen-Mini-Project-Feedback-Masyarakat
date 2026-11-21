import streamlit as st

import sheets
from config import LAYANAN, NAMA_APP

st.set_page_config(page_title=NAMA_APP, page_icon="🏛️", layout="centered")

st.title(NAMA_APP)
st.caption("Prototipe Studi Independen UNESA × Celerates")

st.header("Informasi Pelayanan")
st.info("Daftar layanan di bawah masih contoh dan akan diverifikasi dengan pihak kelurahan.")
for layanan in LAYANAN:
    st.markdown(f"- {layanan}")

st.page_link("pages/1_Beri_Feedback.py", label="Beri Feedback", icon="📝")
st.page_link("pages/2_Dashboard.py", label="Dashboard (operator/pimpinan)", icon="📊")

# --- Bagian sementara untuk pengembang (akan dihapus/disembunyikan di Hari 5) ---
with st.expander("Status sistem (sementara, untuk pengembang)"):
    try:
        cocok, header = sheets.cek_header()
        jumlah = len(sheets.muat_data())
        st.success("Terhubung ke Google Sheets.")
        st.write(f"Jumlah baris data: {jumlah}")
        if cocok:
            st.success("Header Sheet sesuai skema.")
        else:
            st.error("Header Sheet TIDAK sesuai skema.")
            st.write("Header di Sheet:", header)
    except Exception as e:
        st.error(f"Gagal terhubung: {type(e).__name__}")
        st.caption("Cek secrets.toml, nama Sheet/tab, dan apakah Sheet sudah dibagikan ke service account.")
        
        
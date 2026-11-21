"""Login sederhana dua peran (operator dan pimpinan) memakai password di st.secrets."""
import hmac
import time

import streamlit as st

PERAN = {"operator": "operator_password", "pimpinan": "pimpinan_password"}
MAKS_GAGAL = 5
KUNCI_DETIK = 60


def _cocok(masukan: str, asli: str) -> bool:
    return bool(asli) and hmac.compare_digest(masukan.encode(), asli.encode())


def peran_aktif():
    return st.session_state.get("peran")


def wajib_login() -> str:
    """Menampilkan form login bila belum masuk; menghentikan halaman sampai berhasil. Mengembalikan peran."""
    if peran_aktif():
        return peran_aktif()

    st.title("Masuk Dashboard")
    st.write("Halaman ini untuk operator dan pimpinan kelurahan.")
    gagal = st.session_state.get("gagal_login", 0)
    terkunci_sampai = st.session_state.get("terkunci_sampai", 0)
    sisa = int(terkunci_sampai - time.time())
    if sisa > 0:
        st.error(f"Terlalu banyak percobaan. Coba lagi dalam {sisa} detik.")
        st.stop()

    with st.form("form_login"):
        peran = st.selectbox("Masuk sebagai", list(PERAN), format_func=str.capitalize)
        sandi = st.text_input("Kata sandi", type="password")
        masuk = st.form_submit_button("Masuk", type="primary")
    if masuk:
        asli = st.secrets.get("auth", {}).get(PERAN[peran], "")
        if _cocok(sandi, asli):
            st.session_state["peran"] = peran
            st.session_state["gagal_login"] = 0
            st.rerun()
        gagal += 1
        st.session_state["gagal_login"] = gagal
        if gagal >= MAKS_GAGAL:
            st.session_state["terkunci_sampai"] = time.time() + KUNCI_DETIK
            st.session_state["gagal_login"] = 0
        st.error("Kata sandi salah.")
    st.page_link("app.py", label="Kembali ke beranda", icon="🏠")
    st.stop()


def tombol_keluar():
    if st.sidebar.button("Keluar"):
        for k in ("peran", "gagal_login", "terkunci_sampai"):
            st.session_state.pop(k, None)
        st.rerun()

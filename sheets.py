"""Akses Google Sheets (basis data feedback)."""
import gspread
import pandas as pd
import streamlit as st

from config import ASPEK, KOLOM


@st.cache_resource
def _worksheet():
    """Membuka tab Sheet sekali saja lalu dipakai ulang."""
    klien = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    spreadsheet = klien.open(st.secrets["sheet"]["spreadsheet_name"])
    return spreadsheet.worksheet(st.secrets["sheet"]["worksheet"])


def cek_header():
    """Mengembalikan (cocok, header_di_sheet). Dipakai untuk memastikan skema Sheet benar."""
    header = _worksheet().row_values(1)
    return header == KOLOM, header


def tambah_feedback(baris: dict) -> None:
    """Menambah satu baris feedback. 'baris' berisi nilai untuk setiap nama kolom di KOLOM."""
    nilai = [baris.get(kolom, "") for kolom in KOLOM]
    _worksheet().append_row(nilai, value_input_option="RAW")
    muat_data.clear()  # supaya dashboard langsung melihat data terbaru


@st.cache_data(ttl=60)
def muat_data() -> pd.DataFrame:
    """Membaca semua feedback sebagai DataFrame (cache 60 detik = 'near real-time')."""
    rows = _worksheet().get_all_records(numericise_ignore=["all"])
    df = pd.DataFrame(rows, columns=KOLOM)
    for kolom in ASPEK:
        df[kolom] = pd.to_numeric(df[kolom], errors="coerce")
    return df
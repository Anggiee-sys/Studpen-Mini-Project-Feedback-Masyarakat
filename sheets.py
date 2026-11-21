"""Akses Google Sheets (basis data feedback)."""
import gspread
import pandas as pd
import streamlit as st

from config import ASPEK, KOLOM, KOLOM_TL, TAB_TINDAK_LANJUT


@st.cache_resource
def _spreadsheet():
    klien = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    return klien.open(st.secrets["sheet"]["spreadsheet_name"])


@st.cache_resource
def _worksheet():
    """Membuka tab Sheet sekali saja lalu dipakai ulang."""
    return _spreadsheet().worksheet(st.secrets["sheet"]["worksheet"])


@st.cache_resource
def _ws_tindak_lanjut():
    """Tab catatan tindak lanjut; dibuat otomatis (beserta header) bila belum ada."""
    ss = _spreadsheet()
    try:
        ws = ss.worksheet(TAB_TINDAK_LANJUT)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=TAB_TINDAK_LANJUT, rows=200, cols=len(KOLOM_TL))
    if ws.row_values(1) != KOLOM_TL:
        ws.update(range_name="A1", values=[KOLOM_TL])
    return ws


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


def tambah_tindak_lanjut(baris: dict) -> None:
    nilai = [baris.get(k, "") for k in KOLOM_TL]
    _ws_tindak_lanjut().append_row(nilai, value_input_option="RAW")
    muat_tindak_lanjut.clear()


@st.cache_data(ttl=60)
def muat_tindak_lanjut() -> pd.DataFrame:
    rows = _ws_tindak_lanjut().get_all_records(numericise_ignore=["all"])
    return pd.DataFrame(rows, columns=KOLOM_TL)

from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

import analisis as a
import auth
import insight as ins
import sheets
import teks as t
from config import ASPEK, LAYANAN, MAKS_CATATAN, STATUS_TL
from validasi import cek_kualitas_data, deteksi_data_pribadi, ringkas_kualitas

WIB = timezone(timedelta(hours=7))
WARNA = "#2F6F9F"
ASPEK_LABEL = list(ASPEK.values())

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

peran = auth.wajib_login()

st.title("Dashboard Kualitas Pelayanan")
st.caption(f"Masuk sebagai **{peran}** · Kelurahan Geluran")
auth.tombol_keluar()

# ---------- Muat data ----------
try:
    mentah = sheets.muat_data()
except Exception:
    st.error("Data belum dapat dimuat. Coba muat ulang halaman beberapa saat lagi.")
    st.stop()

semua = a.siapkan(mentah)
if semua.empty:
    st.info("Belum ada data feedback.")
    st.stop()

# ---------- Filter (sidebar) ----------
st.sidebar.header("Filter data")
sumber_ada = [s for s in ("real", "uji_coba", "dummy") if s in set(semua["Sumber_Data"])]
sumber_pilih = st.sidebar.multiselect(
    "Sumber data", sumber_ada, default=sumber_ada,
    help="real = feedback warga sungguhan; uji_coba = isian saat pengujian; dummy = simulasi",
)
layanan_pilih = st.sidebar.multiselect("Layanan", LAYANAN, default=LAYANAN)

d = a.siapkan(mentah, sumber=sumber_pilih)
d = d[d["Layanan"].isin(layanan_pilih)].reset_index(drop=True)

if "dummy" in sumber_pilih:
    st.warning("Tampilan mencakup **data dummy (simulasi)**, bukan feedback warga sungguhan.")
if d.empty:
    st.info("Tidak ada data untuk filter yang dipilih.")
    st.stop()

ring = a.ringkasan_umum(d)
if ring["n_kecil"]:
    st.info(f"Jumlah isian baru {ring['jumlah_responden']} (< {a.AMBANG_N_KECIL}); hasil belum stabil.")

# ---------- Tab ----------
nama_tab = ["Ringkasan", "Insight", "Indikator", "Tindak Lanjut"]
if peran == "operator":
    nama_tab += ["Kritik & Saran", "Kualitas Data"]
tab = dict(zip(nama_tab, st.tabs(nama_tab)))

# ----- Ringkasan -----
with tab["Ringkasan"]:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Jumlah isian", ring["jumlah_responden"])
    k2.metric("Skor rata-rata (1-5)", ring["skor_rata_rata"])
    k3.metric("Layanan", ring["jumlah_layanan"])
    k4.metric("Periode", ring["jumlah_periode"])

    st.subheader("Rata-rata per aspek")
    stat = a.statistik_per_aspek(d)
    fig = px.bar(stat, x="Rata-rata", y="Aspek", orientation="h", range_x=[1, 5],
                 color_discrete_sequence=[WARNA], text="Rata-rata")
    fig.update_traces(error_x=dict(type="data", symmetric=False,
                                   array=stat["CI95 atas"] - stat["Rata-rata"],
                                   arrayminus=stat["Rata-rata"] - stat["CI95 bawah"]))
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None)
    st.plotly_chart(fig, width="stretch")
    st.caption("Garis di ujung batang = selang kepercayaan 95%.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Tren per bulan")
        tr = a.tren_periode(d).reset_index()
        panjang = tr.melt(id_vars="Periode", value_vars=ASPEK_LABEL, var_name="Aspek", value_name="Rata-rata")
        f = px.line(panjang, x="Periode", y="Rata-rata", color="Aspek", markers=True, range_y=[1, 5])
        f.update_xaxes(type="category")
        f.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), legend_title=None, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(f, width="stretch")
    with c2:
        st.subheader("Layanan × aspek")
        sl = a.skor_per_layanan(d)
        f = px.imshow(sl[ASPEK_LABEL], text_auto=".2f", color_continuous_scale="RdYlGn",
                      zmin=2.5, zmax=4.5, aspect="auto")
        f.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), coloraxis_showscale=False)
        st.plotly_chart(f, width="stretch")

    st.subheader("Sebaran rating")
    dist = a.distribusi_rating(d).reset_index().melt(id_vars="Aspek", var_name="Rating", value_name="Persen")
    f = px.bar(dist, x="Persen", y="Aspek", color="Rating", orientation="h",
               color_discrete_sequence=["#B5483B", "#E08F5A", "#D9D9D9", "#7FB3D5", "#2F6F9F"],
               category_orders={"Rating": ["1", "2", "3", "4", "5"]})
    f.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title="% responden",
                    legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(f, width="stretch")

# ----- Insight -----
with tab["Insight"]:
    st.caption("Dibuat otomatis dari aturan sederhana (bukan AI): Temuan → Insight → Rekomendasi. "
               "Rekomendasi bersifat saran awal dan perlu dipertimbangkan pihak kelurahan.")
    daftar = ins.buat_insight(d)
    if not daftar:
        st.success("Tidak ada aspek yang menonjol perlu perhatian pada data yang dipilih.")
    for i, x in enumerate(daftar, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. Temuan:** {x['temuan']}")
            st.markdown(f"**Insight:** {x['insight']}")
            st.markdown(f"**Rekomendasi:** {x['rekomendasi']}")

# ----- Indikator (sesuai proposal Bab 4.3) -----
with tab["Indikator"]:
    st.caption(
        "Indikator keberhasilan sesuai proposal (Bab 4.3). Dihitung dari seluruh data dan tidak "
        "terpengaruh filter di samping. Data dummy tidak dihitung sebagai capaian pengguna."
    )
    nyata = a.siapkan(mentah, sumber=["uji_coba", "real"])
    n_real = int((nyata["Sumber_Data"] == "real").sum())
    n_uji = int((nyata["Sumber_Data"] == "uji_coba").sum())
    try:
        tl = sheets.muat_tindak_lanjut()
    except Exception:
        tl = pd.DataFrame(columns=["Status"])
    selesai = int((tl["Status"] == "Selesai").sum()) if len(tl) else 0
    daftar_insight = ins.buat_insight(semua)

    st.subheader("1. Pengguna")
    p1, p2, p3 = st.columns(3)
    p1.metric("A. Feedback terkumpul (uji coba + real)", len(nyata))
    p2.metric("B. Penggunaan sistem", f"{n_real} real / {n_uji} uji coba",
              help="Tanpa identitas, jadi dihitung per pengiriman (1 isian = 1 penggunaan), bukan orang unik.")
    p3.metric("C. Jenis layanan yang mendapat feedback", f"{nyata['Layanan'].nunique()} dari {len(LAYANAN)}")

    st.subheader("2. Data")
    dk_semua = t.tambah_kategori(semua)
    ada_teks = dk_semua[dk_semua["Kategori"].str.len() > 0]
    terkategori = ada_teks[ada_teks["Kategori"].apply(lambda k: k != ["Lainnya"])]
    lengkap = len(semua) / len(mentah) * 100 if len(mentah) else 0
    persen_kat = len(terkategori) / len(ada_teks) * 100 if len(ada_teks) else 0
    q1, q2, q3 = st.columns(3)
    q1.metric("A. Kelengkapan data feedback", f"{lengkap:.0f}%", help="Isian dengan semua rating valid (1-5).")
    q2.metric("B. Kritik/saran berhasil dikategorikan", f"{persen_kat:.0f}%",
              help="Dari teks yang ada, yang masuk kategori selain 'Lainnya' (pengelompokan berbasis kata kunci).")
    q3.metric("C. Data siap dianalisis", f"{len(semua)} baris", help="Skema tetap, modul analisis dan notebook tersedia.")

    st.subheader("3. Monitoring")
    tr = a.tren_periode(semua)
    skor_kini = float(tr["Skor rata-rata"].iloc[-1])
    delta = round(skor_kini - float(tr["Skor rata-rata"].iloc[-2]), 2) if len(tr) > 1 else None
    m1, m2, m3 = st.columns(3)
    m1.metric("A. Dashboard monitoring", "Berfungsi")
    m2.metric(f"B. Skor kualitas {tr.index[-1]}", f"{skor_kini:.2f}", delta=delta,
              help="Kondisi saat ini dan selisih dari periode sebelumnya (tren).")
    m3.metric("C. Insight dihasilkan dari data", "Ya" if daftar_insight else "Belum")

    st.subheader("4. Evaluasi")
    e1, e2, e3 = st.columns(3)
    e1.metric("A. Insight/rekomendasi dihasilkan", len(daftar_insight))
    e2.metric("B. Umpan balik kelurahan", "Setelah demo",
              help="Dikumpulkan lewat demo, lembar validasi, dan surat pernyataan; tidak dihitung otomatis.")
    e3.metric("C. Perbaikan teridentifikasi (tindak lanjut)", f"{len(tl)} catatan", help=f"{selesai} berstatus Selesai.")
    st.caption("Butir yang dihitung dari seluruh sumber data (kelompok 2-4) memakai data dummy bila belum ada data real.")

# ----- Tindak Lanjut -----
with tab["Tindak Lanjut"]:
    try:
        tl = sheets.muat_tindak_lanjut()
    except Exception:
        tl = None
        st.error("Catatan tindak lanjut belum dapat dimuat.")
    if peran == "operator":
        with st.form("form_tl", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            lay = c1.selectbox("Layanan", ["Umum"] + LAYANAN)
            asp = c2.selectbox("Aspek", ASPEK_LABEL + ["Lainnya"])
            sts = c3.selectbox("Status", STATUS_TL)
            cat = st.text_area("Catatan tindak lanjut", max_chars=MAKS_CATATAN,
                               placeholder="Mis. Poster alur persyaratan SKTM dipasang di ruang tunggu.")
            simpan = st.form_submit_button("Simpan catatan", type="primary")
        if simpan:
            if not cat.strip():
                st.error("Catatan tidak boleh kosong.")
            elif deteksi_data_pribadi(cat):
                st.error("Catatan memuat data pribadi. Mohon hapus terlebih dahulu.")
            else:
                try:
                    sheets.tambah_tindak_lanjut({
                        "Timestamp": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
                        "Layanan": lay, "Aspek": asp, "Catatan": cat.strip(), "Status": sts,
                    })
                    st.success("Catatan tersimpan.")
                    st.rerun()
                except Exception:
                    st.error("Catatan belum berhasil disimpan. Coba lagi.")
    if tl is not None:
        if tl.empty:
            st.info("Belum ada catatan tindak lanjut.")
        else:
            st.dataframe(tl.iloc[::-1], width="stretch", hide_index=True)

# ----- Khusus operator -----
if peran == "operator":
    with tab["Kritik & Saran"]:
        dk = t.tambah_kategori(d)
        ada = dk[dk["Kategori"].str.len() > 0]
        if ada.empty:
            st.info("Belum ada kritik/saran tertulis.")
        else:
            hk = t.hitung_kategori(dk)
            f = px.bar(hk, x="Jumlah", y="Kategori", orientation="h", color_discrete_sequence=[WARNA], text="Jumlah")
            f.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"), yaxis_title=None)
            st.plotly_chart(f, width="stretch")
            st.caption("Pengelompokan memakai kata kunci (bukan AI); satu teks bisa masuk lebih dari satu kategori.")
            pilih = st.selectbox("Lihat teks per kategori", ["Semua"] + hk["Kategori"].tolist())
            tampil = ada if pilih == "Semua" else ada[ada["Kategori"].apply(lambda k: pilih in k)]
            tampil = tampil.assign(Kategori=tampil["Kategori"].apply(", ".join))
            st.dataframe(tampil[["Timestamp", "Layanan", "Kategori", "Nada", "Kritik_Saran"]].iloc[::-1],
                         width="stretch", hide_index=True)

    with tab["Kualitas Data"]:
        st.write(ringkas_kualitas(cek_kualitas_data(mentah)))
        st.write("Jumlah isian per sumber data:")
        st.dataframe(mentah["Sumber_Data"].value_counts().rename_axis("Sumber_Data").reset_index(name="Jumlah"),
                     hide_index=True)

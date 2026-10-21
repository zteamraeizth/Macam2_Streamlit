import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(
    page_title="Simulasi Pembayaran Tagihan & Pajak",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Simulasi Pembayaran & Pemotongan Pajak")
st.caption("Perhitungan DPP Murni (PPh), DPP Nilai Lain (PPN 12%), dan Nilai Bersih")

st.markdown("---")

# ---------------------------------------------------------
# INPUT UTAMA
# ---------------------------------------------------------
st.subheader("1. Input Nilai Tagihan")
total_tagihan = st.number_input(
    "Masukkan Nilai Total Tagihan / Nilai Kotor (Rp):",
    min_value=0.0,
    value=10000000.0,
    step=100000.0,
    format="%.2f"
)

st.markdown("---")

# ---------------------------------------------------------
# OPSI PPN
# ---------------------------------------------------------
st.subheader("2. Pengaturan PPN")
is_ppn = st.radio("Apakah Transaksi Dikenakan PPN?", ["Tidak", "Ya"], horizontal=True)

dpp_murni = 0.0
dpp_nilai_lain = 0.0
nilai_ppn = 0.0

if is_ppn == "Ya":
    # Berdasarkan PPN 12% dengan DPP Nilai Lain (11/12):
    # PPN Efektif = 12% * (11/12) * Total Tagihan = 11% * Total Tagihan
    # Maka DPP Murni (sebelum PPN) = Total Tagihan / 1.11
    dpp_murni = total_tagihan / 1.11
    dpp_nilai_lain = (11 / 12) * total_tagihan
    nilai_ppn = 0.12 * dpp_nilai_lain
else:
    dpp_murni = total_tagihan
    dpp_nilai_lain = 0.0
    nilai_ppn = 0.0

# ---------------------------------------------------------
# OPSI PPh
# ---------------------------------------------------------
st.subheader("3. Pengaturan Potongan PPh")
is_pph = st.radio("Apakah Dikenakan Potongan PPh?", ["Tidak", "Ya"], horizontal=True)

tarif_pph = 0.0
jenis_pph = "-"
nilai_pph = 0.0
has_npwp = True

if is_pph == "Ya":
    col_pph1, col_pph2 = st.columns(2)
    with col_pph1:
        jenis_pph = st.selectbox(
            "Pilih Jenis PPh:",
            [
                "PPh 23 - Jasa / Sewa Harta (2%)",
                "PPh 23 - Royalti / Hadiah (15%)",
                "PPh 22 - Pembelian Barang (1.5%)",
                "PPh 4 ayat 2 - Sewa Tanah/Bangunan (10%)",
                "PPh 4 ayat 2 - Jasa Konstruksi / Pelaksanaan (1.75%)",
                "PPh 4 ayat 2 - Jasa Konstruksi / Pelaksanaan Standar (2.65%)"
            ]
        )
    
    with col_pph2:
        npwp_status = st.radio("Memiliki NPWP?", ["Ya", "Tidak"], horizontal=True)
        has_npwp = True if npwp_status == "Ya" else False

    # Tarif Dasar
    if "PPh 23 - Jasa" in jenis_pph:
        tarif_pph = 0.02
    elif "PPh 23 - Royalti" in jenis_pph:
        tarif_pph = 0.15
    elif "PPh 22 - Pembelian" in jenis_pph:
        tarif_pph = 0.015
    elif "PPh 4 ayat 2 - Sewa" in jenis_pph:
        tarif_pph = 0.10
    elif "1.75%" in jenis_pph:
        tarif_pph = 0.0175
    elif "2.65%" in jenis_pph:
        tarif_pph = 0.0265

    # Penalti tanpa NPWP (Khusus PPh 23 dan PPh 22)
    if not has_npwp:
        if "PPh 23" in jenis_pph or "PPh 22" in jenis_pph:
            tarif_pph *= 2.0
            st.warning("⚠️ Tarif naik 100% (2x lipat) karena tidak memiliki NPWP.")

    # PPh dihitung dari DPP Murni
    nilai_pph = dpp_murni * tarif_pph

st.markdown("---")

# ---------------------------------------------------------
# KALKULASI BERSIH & REKONSILIASI
# ---------------------------------------------------------
# Nilai Bersih yang dibayarkan = Total Tagihan - Potongan PPh - Nilai PPN
# (Atau jika PPN dibayarkan terpisah, disesuaikan dengan skema pembayarnya)
nilai_bersih = total_tagihan - nilai_pph - nilai_ppn

# Check Balance: Total Tagihan = Nilai Bersih + Nilai PPh + Nilai PPN
total_sistem = nilai_bersih + nilai_pph + nilai_ppn
selisih = abs(total_tagihan - total_sistem)
status_match = "✅ MATCH" if selisih < 0.01 else f"❌ MISMATCH (Selisih: Rp {selisih:,.2f})"

# ---------------------------------------------------------
# TAMPILAN TABEL
# ---------------------------------------------------------
st.subheader("📊 Tabel Rincian Pembayaran")

# Data Rincian Utama
data_rincian = {
    "Komponen Perhitungan": [
        "Nilai Total Tagihan (Kotor)",
        "DPP Murni (Dasar PPh)",
        "DPP Nilai Lain (11/12)",
        "Nilai PPN (12%)",
        f"Potongan PPh ({jenis_pph if is_pph == 'Ya' else 'Tanpa PPh'})",
        "💰 Nilai Total Bersih (Dibayarkan)"
    ],
    "Keterangan / Tarif": [
        "Nilai Kotor Awal",
        "Tagihan ÷ 1.11" if is_ppn == "Ya" else "Sama dengan Tagihan",
        "11/12 × Tagihan" if is_ppn == "Ya" else "Tidak ada PPN",
        "12% × DPP Nilai Lain (11% Efektif)" if is_ppn == "Ya" else "0%",
        f"Tarif: {tarif_pph*100:.2f}% × DPP Murni" if is_pph == "Ya" else "0%",
        "Total Tagihan - PPh - PPN"
    ],
    "Nilai (Rp)": [
        f"Rp {total_tagihan:,.2f}",
        f"Rp {dpp_murni:,.2f}",
        f"Rp {dpp_nilai_lain:,.2f}",
        f"Rp {nilai_ppn:,.2f}",
        f"Rp {nilai_pph:,.2f}",
        f"Rp {nilai_bersih:,.2f}"
    ]
}

df_rincian = pd.DataFrame(data_rincian)
st.table(df_rincian)

st.markdown("---")

# Tabel Check Balance
st.subheader("🔄 Tabel Pencocokan Sistem (Check Balance)")
st.caption("Formula: Nilai Total Tagihan = Nilai Bersih + Nilai PPh + Nilai PPN")

data_check = {
    "Parameter": [
        "Total Tagihan Input", 
        "Total Kalkulasi Sistem (Bersih + PPh + PPN)", 
        "Status Pencocokan"
    ],
    "Nilai / Hasil": [
        f"Rp {total_tagihan:,.2f}",
        f"Rp {total_sistem:,.2f}",
        status_match
    ]
}

df_check = pd.DataFrame(data_check)
st.table(df_check)

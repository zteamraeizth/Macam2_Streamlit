import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kalkulator Pajak Simpel", page_icon="🧮", layout="centered")

st.title("🧮 Kalkulator Pajak Ringkas")

# ---------------------------------------------------------
# INPUT FORM DALAM SATU BARIS / TAMPILAN RAPI
# ---------------------------------------------------------
col_in1, col_in2, col_in3 = st.columns([2, 1, 1])

with col_in1:
    dpp_murni = st.number_input(
        "DPP Murni (Rp):",
        min_value=0.0,
        value=9735490.0,
        step=1000.0,
        format="%.2f"
    )

with col_in2:
    is_ppn = st.radio("Dikenakan PPN?", ["Ya", "Tidak"], horizontal=True)

with col_in3:
    is_pph = st.radio("Potongan PPh?", ["Ya", "Tidak"], horizontal=True)

# Opsi Lanjutan PPh (Hanya Muncul Jika PPh = Ya)
jenis_pph = "-"
tarif_pph = 0.0

if is_pph == "Ya":
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        jenis_pph = st.selectbox(
            "Jenis PPh:",
            [
                "PPh 23 - Jasa (2%)",
                "PPh 23 - Royalti (15%)",
                "PPh 22 - Pembelian (1.5%)",
                "PPh 4(2) - Sewa (10%)",
                "PPh 4(2) - Konstruksi (1.75%)",
                "PPh 4(2) - Konstruksi Std (2.65%)"
            ]
        )
    with col_sub2:
        has_npwp = st.radio("Ada NPWP?", ["Ya", "Tidak"], horizontal=True)

    # Tarif Dasar
    if "PPh 23 - Jasa" in jenis_pph:
        tarif_pph = 0.02
    elif "PPh 23 - Royalti" in jenis_pph:
        tarif_pph = 0.15
    elif "PPh 22 - Pembelian" in jenis_pph:
        tarif_pph = 0.015
    elif "PPh 4(2) - Sewa" in jenis_pph:
        tarif_pph = 0.10
    elif "1.75%" in jenis_pph:
        tarif_pph = 0.0175
    elif "2.65%" in jenis_pph:
        tarif_pph = 0.0265

    if has_npwp == "Tidak" and ("PPh 23" in jenis_pph or "PPh 22" in jenis_pph):
        tarif_pph *= 2.0

# ---------------------------------------------------------
# KALKULASI DENGAN PEMBULATAN
# ---------------------------------------------------------
if is_ppn == "Ya":
    dpp_nilai_lain = round((11 / 12) * dpp_murni)
    nilai_ppn = round(0.12 * dpp_nilai_lain)
else:
    dpp_nilai_lain = 0.0
    nilai_ppn = 0.0

total_tagihan = dpp_murni + nilai_ppn
nilai_pph = round(dpp_murni * tarif_pph) if is_pph == "Ya" else 0.0
nilai_bersih = total_tagihan - nilai_pph - nilai_ppn

# Match Check
total_sistem = nilai_bersih + nilai_pph + nilai_ppn
selisih = abs(total_tagihan - total_sistem)
status_match = "✅ MATCH" if selisih < 0.01 else f"❌ MISMATCH (Selisih: Rp {selisih:,.0f})"

st.markdown("---")

# ---------------------------------------------------------
# TABEL RINGKASAN & REKONSILIASI
# ---------------------------------------------------------
st.caption("### 📊 Rincian Perhitungan")

data_ringkas = {
    "Komponen": [
        "1. DPP Murni",
        "2. DPP Nilai Lain (11/12)",
        "3. Nilai PPN (12%)",
        "4. Total Tagihan (Kotor)",
        f"5. Potongan PPh ({jenis_pph})",
        "6. 💰 Nilai Bersih (Dibayarkan)"
    ],
    "Nilai (Rp)": [
        f"Rp {dpp_murni:,.0f}",
        f"Rp {dpp_nilai_lain:,.0f}",
        f"Rp {nilai_ppn:,.0f}",
        f"Rp {total_tagihan:,.0f}",
        f"Rp {nilai_pph:,.0f}",
        f"Rp {nilai_bersih:,.0f}"
    ]
}

st.table(pd.DataFrame(data_ringkas))

# Status Pencocokan Sistem
st.caption(f"**Check Balance:** `Tagihan Kotor ({total_tagihan:,.0f}) = Bersih ({nilai_bersih:,.0f}) + PPh ({nilai_pph:,.0f}) + PPN ({nilai_ppn:,.0f})` **--> {status_match}**")

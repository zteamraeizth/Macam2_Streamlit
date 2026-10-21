import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Simulasi Pembayaran Tagihan & Pajak",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Simulasi Pembayaran & Pemotongan Pajak")
st.caption("Hitung DPP, PPN 12% (DPP Nilai Lain), PPh (23/22/4(2)), dan Nilai Bersih Tagihan")

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

dpp = 0.0
dpp_nilai_lain = 0.0
tarif_ppn_efektif = 0.12
nilai_ppn = 0.0

if is_ppn == "Ya":
    # Berdasarkan tarif PPN 12%:
    # Total Tagihan (Kotor) = DPP + PPN (12% dari DPP Nilai Lain)
    # DPP Nilai Lain = (11/12) * Total Tagihan
    # PPN = 12% * DPP Nilai Lain
    dpp_nilai_lain = (11 / 12) * total_tagihan
    nilai_ppn = 0.12 * dpp_nilai_lain
    dpp = dpp_nilai_lain  # DPP Utama yang digunakan sebagai acuan
else:
    dpp = total_tagihan
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

    # Penentuan Tarif PPh Dasar
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

    # Penyesuaian tanpa NPWP (Tarif 100% lebih tinggi untuk PPh 23, 100% untuk PPh 22, PPh 4(2) final tidak berubah)
    if not has_npwp:
        if "PPh 23" in jenis_pph:
            tarif_pph *= 2.0  # Penalti 100%
            st.warning("⚠️ Karena tidak ber-NPWP, tarif PPh 23 naik 100% (2x lipat).")
        elif "PPh 22" in jenis_pph:
            tarif_pph *= 2.0  # Penalti 100%
            st.warning("⚠️ Karena tidak ber-NPWP, tarif PPh 22 naik 100% (2x lipat).")

    # Hitung Nilai PPh berbasis DPP
    nilai_pph = dpp * tarif_pph

st.markdown("---")

# ---------------------------------------------------------
# KALKULASI & HASIL
# ---------------------------------------------------------
# Total Bersih / Nilai Dibayarkan = Total Tagihan - Potongan PPh
# (Jika tagihan mencakup PPN, PPN dibayarkan/diakui sesuai DPP + PPN, tetapi potongan PPh mengurangi kas yang dibayarkan)
nilai_bersih = total_tagihan - nilai_pph

st.subheader("📊 Rincian Hasil Perhitungan")

col1, col2 = st.columns(2)

with col1:
    st.metric("Nilai Total Tagihan (Kotor)", f"Rp {total_tagihan:,.2f}")
    st.metric("DPP / DPP Nilai Lain", f"Rp {dpp:,.2f}")
    if is_ppn == "Ya":
        st.caption(f"DPP Nilai Lain (11/12): Rp {dpp_nilai_lain:,.2f}")
        st.metric("Nilai PPN (12%)", f"Rp {nilai_ppn:,.2f}")
    else:
        st.metric("Nilai PPN", "Rp 0.00 (Tidak Dikenakan)")

with col2:
    if is_pph == "Ya":
        st.metric(f"Potongan PPh ({tarif_pph*100:.2f}%)", f"Rp {nilai_pph:,.2f}")
        st.caption(f"Jenis: {jenis_pph}")
    else:
        st.metric("Potongan PPh", "Rp 0.00 (Tidak Dikenakan)")
    
    st.metric("💰 Nilai Total Bersih (Dibayarkan)", f"Rp {nilai_bersih:,.2f}")

st.markdown("---")

# ---------------------------------------------------------
# PENCOCOKAN SISTEM / REKONSILIASI
# ---------------------------------------------------------
st.subheader("🔄 Pencocokan Sistem (Check Balance)")

# Sesuai formula persamaannya: Total Tagihan = Nilai Bersih + Nilai PPh
# Atau Total Kotor = Nilai Bersih + Nilai PPh (di mana Total Kotor sudah include PPN jika ada)
total_sistem = nilai_bersih + nilai_pph
selisih = abs(total_tagihan - total_sistem)

st.write("**Formula:** `Nilai Total Tagihan = Nilai Bersih + Nilai PPh`")

col_chk1, col_chk2, col_chk3 = st.columns(3)
col_chk1.write(f"**Total Tagihan Input:**\nRp {total_tagihan:,.2f}")
col_chk2.write(f"**Total Kalkulasi Sistem:**\nRp {total_sistem:,.2f}")

if selisih < 0.01:
    col_chk3.success("✅ **MATCH / COCOK**")
else:
    col_chk3.error(f"❌ **MISMATCH (Selisih: Rp {selisih:,.2f})**")

# Detail Ringkasan Akuntansi
with st.expander("📌 Lihat Ringkasan Rekonsiliasi Akuntansi"):
    st.json({
        "Total Tagihan (Kotor)": f"Rp {total_tagihan:,.2f}",
        "DPP": f"Rp {dpp:,.2f}",
        "DPP Nilai Lain (11/12)": f"Rp {dpp_nilai_lain:,.2f}" if is_ppn == "Ya" else "Rp 0.00",
        "Tarif PPN Efektif": "12%" if is_ppn == "Ya" else "0%",
        "Nilai PPN": f"Rp {nilai_ppn:,.2f}",
        "Jenis PPh": jenis_pph if is_pph == "Ya" else "Tanpa PPh",
        "Tarif PPh": f"{tarif_pph*100:.2f}%" if is_pph == "Ya" else "0%",
        "Nilai Potongan PPh": f"Rp {nilai_pph:,.2f}",
        "Nilai Total Bersih (Take Home)": f"Rp {nilai_bersih:,.2f}",
        "Hasil Check Balance": "SEIMBANG" if selisih < 0.01 else "TIDAK SEIMBANG"
    })

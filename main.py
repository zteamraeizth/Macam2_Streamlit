import streamlit as st

st.set_page_config(
    page_title="Portal Aplikasi Internal",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ Dashboard Portal Aplikasi Streamlit")
st.write(
    "Selamat datang! Silakan pilih aplikasi yang ingin Anda gunakan melalui **sidebar menu di sebelah kiri**."
)

st.markdown("---")

# Menampilkan Ringkasan Aplikasi yang Tersedia
col1, col2 = st.columns(2)

with col1:
    st.info("### 📑 Aplikasi Perjalanan Dinas & Keuangan")
    st.markdown("""
    - **ID Perjadin**
    - **Data ST**
    - **Status Perjadin**
    - **E-Perjadin**
    - **SPP vs DAPEM (Pencocokan Dokumen)**
    """)

with col2:
    st.info("### 🛠️ Utilitas & Tools Administrative")
    st.markdown("""
    - **Konverter Uang ke Terbilang**
    - **Generator QR Code**
    - **Pembuat Undangan**
    - **Watermark Tool**
    - **Detail Modal & Arsip Data**
    """)

st.caption("Pilih menu di sidebar untuk mulai menggunakan fitur.")
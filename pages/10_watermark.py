import io
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PDF Watermark & Encryptor", layout="centered")

st.title("📄 PDF Watermark & Encryption Tool")
st.write(
    "Upload banyak file PDF sekaligus untuk diberi watermark dan dikunci dengan password."
)

# Gunakan session_state untuk membuat key dinamis agar file uploader bisa di-reset
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

# 1. Upload file PDF dengan key dari session_state
uploaded_files = st.file_uploader(
    "Upload File PDF (Bisa Banyak)",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"pdf_uploader_{st.session_state['uploader_key']}",
)

# 2. Pengaturan Watermark & Password
st.subheader("⚙️ Pengaturan")
watermark_text = st.text_input("Teks Watermark", value="RAHASIA / CONFIDENTIAL")

use_password = st.checkbox("Gunakan Password untuk Mengunci PDF?")
pdf_password = ""

if use_password:
    pdf_password = st.text_input(
        "Masukkan Password PDF",
        type="password",
        help="Password ini akan digunakan untuk membuka file PDF hasil download.",
    )


def create_watermark_pdf(text, width, height):
    """Membuat PDF layer watermark transparan secara dinamis."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))

    can.setFillColor(Color(0.5, 0.5, 0.5, alpha=0.3))
    can.setFont("Helvetica-Bold", 36)

    can.saveState()
    can.translate(width / 2, height / 2)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()

    can.save()
    packet.seek(0)
    return PdfReader(packet)


# 3. Tombol Aksi (Proses dan Clear)
if uploaded_files:
    col1, col2 = st.columns([3, 1])

    with col1:
        process_btn = st.button("🚀 Proses Semua PDF", use_container_width=True)

    with col2:
        # Tombol untuk menghapus semua file yang di-upload
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state["uploader_key"] += 1
            st.rerun()

    if process_btn:
        if use_password and not pdf_password:
            st.error("Silakan isi password terlebih dahulu!")
        else:
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for uploaded_file in uploaded_files:
                    reader = PdfReader(uploaded_file)
                    writer = PdfWriter()

                    for page in reader.pages:
                        page_width = float(page.mediabox.width)
                        page_height = float(page.mediabox.height)

                        wm_pdf = create_watermark_pdf(
                            watermark_text, page_width, page_height
                        )
                        wm_page = wm_pdf.pages[0]

                        page.merge_page(wm_page)
                        writer.add_page(page)

                    if use_password and pdf_password:
                        writer.encrypt(pdf_password)

                    pdf_output = io.BytesIO()
                    writer.write(pdf_output)

                    zip_file.writestr(
                        f"{uploaded_file.name}",
                        pdf_output.getvalue(),
                    )

            st.success("✅ Semua file PDF berhasil diproses!")
            st.download_button(
                label="📦 Download Semua PDF (.ZIP)",
                data=zip_buffer.getvalue(),
                file_name="pdf_watermarked_and_locked.zip",
                mime="application/zip",
            )
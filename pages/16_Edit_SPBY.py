import io
import streamlit as st
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="PDF Direct Editor", layout="wide")

st.title("📄 PDF Direct Text Editor (SPBY)")
st.write("Upload file PDF, edit teksnya secara langsung di Streamlit, lalu buat PDF baru.")

# 1. Upload File PDF
uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    # Membaca PDF menggunakan PyMuPDF (fitz)
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Ekstraksi teks dari seluruh halaman
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text() + "\n"

    st.subheader("📝 Area Edit Teks PDF")
    
    # Text area untuk menyunting konten PDF secara langsung
    edited_text = st.text_area(
        "Silahkan sesuaikan/edit teks di bawah ini:",
        value=extracted_text,
        height=400
    )

    # 2. Re-generate PDF Baru Menggunakan ReportLab
    if st.button("🔄 Buat & Simpan PDF Baru"):
        if edited_text.strip():
            with st.spinner("Memproses pembuatan PDF baru..."):
                pdf_buffer = io.BytesIO()
                doc_pdf = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    rightMargin=36,
                    leftMargin=36,
                    topMargin=36,
                    bottomMargin=36
                )
                
                styles = getSampleStyleSheet()
                # Kustomisasi gaya teks agar rapi
                normal_style = ParagraphStyle(
                    'PDFStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    fontName='Helvetica'
                )

                story = []
                # Memproses baris demi baris menjadi paragraf PDF
                lines = edited_text.split('\n')
                for line in lines:
                    if line.strip():
                        # Mengamankan karakter khusus HTML/XML untuk ReportLab
                        safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(safe_line, normal_style))
                    else:
                        story.append(Spacer(1, 8))

                # Build PDF ke memori buffer
                doc_pdf.build(story)
                pdf_buffer.seek(0)

                st.success("PDF baru berhasil diproses!")
                
                # Button Download
                st.download_button(
                    label="📥 Download PDF Hasil Edit",
                    data=pdf_buffer,
                    file_name="SPBY_Edited.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Teks tidak boleh kosong.")

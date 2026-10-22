import os
import subprocess
import tempfile
import platform
import streamlit as st
from pdf2docx import Converter
from docx import Document
from st_quill import st_quill

st.title("📄 PDF & Word Visual Editor (SPBY)")
st.write("Upload PDF, edit dokumen secara visual seperti di Word (layout, format, tabel), lalu simpan kembali ke PDF.")

# 1. Upload File PDF
uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    # Simpan file sementara
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(uploaded_file.read())
        tmp_pdf_path = tmp_pdf.name

    tmp_docx_path = tmp_pdf_path.replace(".pdf", ".docx")

    # Konversi PDF ke DOCX
    with st.spinner("Mengekstrak dan mengonversi isi PDF..."):
        cv = Converter(tmp_pdf_path)
        cv.convert(tmp_docx_path, start=0, end=None)
        cv.close()

    # Baca isi teks dari DOCX
    doc = Document(tmp_docx_path)
    initial_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])

    st.subheader("📝 Visual Word Editor")
    st.info("Anda dapat mengedit format teks, cetak tebal/miring, daftar bullet, alignment, dll. secara langsung di bawah ini:")

    # 2. Rich Text / WYSIWYG Editor
    edited_content = st_quill(
        value=initial_text,
        html=True,
        toolbar=[
            ["bold", "italic", "underline", "strike"],
            [{"header": [1, 2, 3, False]}],
            [{"list": "ordered"}, {"list": "bullet"}],
            [{"align": []}],
            ["clean"]
        ],
        key="quill_editor"
    )

    # 3. Simpan & Konversi ke PDF
    if st.button("🔄 Simpan Perubahan & Buat PDF Baru"):
        if edited_content:
            with st.spinner("Memproses konversi ke PDF..."):
                # Buat file DOCX baru dari hasil editan
                new_doc = Document()
                # Memisahkan paragraf berdasarkan tag HTML atau newline
                import re
                clean_text = re.sub('<[^<]+?>', '', edited_content) # pembersihan tag HTML sederhana
                
                for line in clean_text.split("\n"):
                    if line.strip():
                        new_doc.add_paragraph(line)

                output_docx = "spby_edited.docx"
                output_pdf = "spby_edited.pdf"
                new_doc.save(output_docx)

                # Deteksi Sistem Operasi (Windows vs Linux/Streamlit Cloud)
                try:
                    if platform.system() == "Windows":
                        from docx2pdf import convert
                        convert(output_docx, output_pdf)
                    else:
                        # Di Linux / Streamlit Cloud menggunakan LibreOffice
                        subprocess.run([
                            "soffice", "--headless", "--convert-to", "pdf",
                            output_docx, "--outdir", "."
                        ], check=True)

                    with open(output_pdf, "rb") as f:
                        st.success("Dokumen berhasil diperbarui!")
                        st.download_button(
                            label="📥 Download PDF SPBY Hasil Edit",
                            data=f,
                            file_name="SPBY_Edited.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Gagal melakukan konversi ke PDF: {e}")

    # Clean up file sementara
    if os.path.exists(tmp_pdf_path):
        os.remove(tmp_pdf_path)
    if os.path.exists(tmp_docx_path):
        os.remove(tmp_docx_path)

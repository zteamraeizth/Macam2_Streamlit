import io
import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

st.set_page_config(
    page_title="PDF First Page Merger", page_icon="📄", layout="centered"
)

st.title("📄 Merge Halaman 1 PDF")
st.write(
    "Unggah beberapa file PDF, dan aplikasi ini akan mengambil **halaman pertama saja** dari setiap file, lalu menggabungkannya menjadi satu dokumen PDF baru."
)

# File uploader untuk menerima banyak file PDF
uploaded_files = st.file_uploader(
    "Pilih file PDF", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
  st.info(f"Total file diunggah: {len(uploaded_files)}")

  if st.button("Gabungkan Halaman 1 PDF", type="primary"):
    with st.spinner("Sedang memproses..."):
      merger = PdfMerger()
      output_stream = io.BytesIO()

      try:
        for uploaded_file in uploaded_files:
          reader = PdfReader(uploaded_file)

          # Pastikan file PDF memiliki minimal 1 halaman
          if len(reader.pages) > 0:
            writer = PdfWriter()
            # Ambil halaman ke-0 (halaman pertama)
            writer.add_page(reader.pages[0])

            # Simpan sementara ke dalam BytesIO
            temp_pdf = io.BytesIO()
            writer.write(temp_pdf)
            temp_pdf.seek(0)

            # Tambahkan ke merger
            merger.append(temp_pdf)

        # Tulis hasil gabungan ke output stream
        merger.write(output_stream)
        merger.close()
        output_stream.seek(0)

        st.success("Berhasil menggabungkan halaman pertama dari semua PDF!")

        # Tombol untuk mengunduh hasil PDF
        st.download_button(
            label="📥 Unduh PDF Hasil Gabungan",
            data=output_stream,
            file_name="merged_first_pages.pdf",
            mime="application/pdf",
        )

      except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses PDF: {e}")

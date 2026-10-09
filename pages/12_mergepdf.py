import io
import streamlit as st
from pypdf import PdfWriter

st.set_page_config(page_title="PDF Merger", page_icon="📄", layout="centered")

st.title("📄 PDF Merger Multi-File")
st.write("Unggah beberapa file PDF, atur urutannya, dan gabungkan menjadi satu file.")

# 1. File Uploader
uploaded_files = st.file_uploader(
    "Pilih atau drag-and-drop file PDF di sini",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"**Total file diunggah:** {len(uploaded_files)}")
    
    # Mode Pengurutan
    sort_option = st.radio(
        "Metode Pengurutan File:",
        ("Sesuai Urutan Upload / Custom", "Abjad A-Z", "Abjad Z-A"),
        horizontal=True
    )
    
    # Salin list file agar bisa dimanipulasi
    files_to_process = list(uploaded_files)
    
    if sort_option == "Abjad A-Z":
        files_to_process.sort(key=lambda x: x.name)
    elif sort_option == "Abjad Z-A":
        files_to_process.sort(key=lambda x: x.name, reverse=True)
    
    st.subheader("Urutan File Saat Ini:")
    
    # Menampilkan daftar file dan opsi penyesuaian urutan manual
    ordered_files = []
    for i, file in enumerate(files_to_process):
        col1, col2 = st.columns([1, 4])
        with col1:
            # Dropdown untuk memilih posisi urutan kustom
            new_pos = st.selectbox(
                f"Posisi file {i+1}",
                options=list(range(1, len(files_to_process) + 1)),
                index=i,
                key=f"pos_{file.name}_{i}",
                label_visibility="collapsed"
            )
        with col2:
            st.text(f"{file.name}")
        
        ordered_files.append((new_pos, file))
    
    # Sort berdasarkan posisi manual yang dipilih user
    ordered_files.sort(key=lambda x: x[0])
    final_file_list = [item[1] for item in ordered_files]
    
    st.divider()
    
    # Nama file output
    output_filename = st.text_input("Nama file hasil penggabungan:", value="merged_document.pdf")
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"
        
    # Tombol Merge
    if st.button("🚀 Gabungkan PDF", type="primary"):
        try:
            merger = PdfWriter()
            
            for pdf_file in final_file_list:
                merger.append(pdf_file)
                
            # Simpan ke byte buffer di memori
            output_pdf = io.BytesIO()
            merger.write(output_pdf)
            merger.close()
            output_pdf.seek(0)
            
            st.success("PDF berhasil digabungkan!")
            
            # Tombol Download
            st.download_button(
                label="📥 Download PDF Hasil Penggabungan",
                data=output_pdf,
                file_name=output_filename,
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Terjadi kesalahan saat menggabungkan PDF: {e}")
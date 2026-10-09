import io
import fitz  # PyMuPDF
import streamlit as st
from PIL import Image

st.set_page_config(page_title="PDF Compressor", page_icon="🗜️", layout="centered")

st.title("🗜️ PDF Compressor Multi-Level")
st.write("Pilih tingkat kompresi untuk mengecilkan ukuran file PDF Anda.")

uploaded_file = st.file_uploader("Unggah File PDF", type=["pdf"])

if uploaded_file:
    # Tampilkan Ukuran Asli File
    file_bytes = uploaded_file.getvalue()
    original_size_mb = len(file_bytes) / (1024 * 1024)
    
    st.info(f"📄 **Nama File:** {uploaded_file.name} | **Ukuran Asli:** {original_size_mb:.2f} MB")

    # 1. Pilih Tingkat Kompresi
    compress_level = st.radio(
        "Tingkat Kompresi:",
        ("Small Compress (Kualitas Tinggi)", "Medium Compress (Keseimbangan)", "Hard Compress (Ukuran Paling Kecil)"),
        index=1
    )

    st.divider()

    # Nama File Output
    output_filename = st.text_input("Nama File Output:", value=f"compressed_{uploaded_file.name}")
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"

    if st.button("🚀 Kompres PDF", type="primary"):
        try:
            # Pengaturan berdasarkan level kompresi
            if "Small" in compress_level:
                img_quality = 80
                dpi_target = 150
            elif "Medium" in compress_level:
                img_quality = 60
                dpi_target = 100
            else:  # Hard Compress
                img_quality = 35
                dpi_target = 72

            # Buka PDF dari memory menggunakan PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            # Kompresi gambar internal di dalam PDF
            for page in doc:
                image_list = page.get_images(full=True)
                for img_info in image_list:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    try:
                        # Re-encode gambar menggunakan Pillow dengan kualitas lebih rendah
                        img = Image.open(io.BytesIO(image_bytes))
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Resize gambar jika dimensinya terlalu besar
                        max_dim = int(dpi_target * 11)  # Estimasi max piksel per sisi
                        if max(img.size) > max_dim:
                            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=img_quality, optimize=True)
                        compressed_img_bytes = buffer.getvalue()

                        # Ganti stream gambar lama di PDF
                        page.replace_image(xref, stream=compressed_img_bytes)
                    except Exception:
                        continue  # Abaikan jika ada format gambar tidak didukung

            # Simpan PDF dengan optimasi bawaan PyMuPDF (garbage collection, deflate, clean unused)
            output_buffer = io.BytesIO()
            doc.save(
                output_buffer,
                garbage=4,
                deflate=True,
                clean=True
            )
            doc.close()

            output_buffer.seek(0)
            compressed_size_mb = len(output_buffer.getvalue()) / (1024 * 1024)
            reduction_pct = ((original_size_mb - compressed_size_mb) / original_size_mb) * 100

            st.success("✅ Kompresi Berhasil!")
            
            col1, col2 = st.columns(2)
            col1.metric("Ukuran Baru", f"{compressed_size_mb:.2f} MB")
            col2.metric("Penghematan Ukuran", f"{reduction_pct:.1f}%")

            st.download_button(
                label="📥 Download PDF Hasil Kompresi",
                data=output_buffer,
                file_name=output_filename,
                mime="application/pdf",
                type="primary"
            )

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
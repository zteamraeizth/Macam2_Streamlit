import io
import re
import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(page_title="PDF Tools: Split, Reorder or Delete", page_icon="✂️", layout="centered")

st.title("✂️ Split, Reorder or Delete PDF Pages")

uploaded_file = st.file_uploader("Unggah File PDF", type=["pdf"])

def parse_page_range(range_str, total_pages):
    """Fungsi helper untuk memproses input halaman seperti '1, 3-5, even, odd, reverse, last'"""
    pages = []
    range_str = range_str.strip().lower()
    
    if range_str == "even":
        return [i for i in range(1, total_pages + 1) if i % 2 == 0]
    elif range_str == "odd":
        return [i for i in range(1, total_pages + 1) if i % 2 != 0]
    elif range_str == "reverse":
        return list(range(total_pages, 0, -1))
    elif range_str == "last":
        return [total_pages]

    parts = range_str.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                pages.extend(range(start, end + 1))
            except ValueError:
                pass
        elif part.isdigit():
            pages.append(int(part))
        elif part == "last":
            pages.append(total_pages)

    # Validasi rentang halaman
    valid_pages = [p for p in pages if 1 <= p <= total_pages]
    return valid_pages


if uploaded_file:
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    
    st.info(f"There are **{total_pages}** pages in **{uploaded_file.name}**")
    
    # 1. Mode Operasi Utama (Radio Option)
    action = st.radio(
        "Pilih Aksi:",
        ("Split Pages From", "Reorder Pages", "Delete Pages"),
        index=0
    )
    
    # Parameter Berdasarkan Pilihan
    if action == "Split Pages From":
        col1, col2 = st.columns(2)
        with col1:
            from_page = st.number_input("From", min_value=1, max_value=total_pages, value=1)
        with col2:
            to_page = st.number_input("To", min_value=1, max_value=total_pages, value=min(1, total_pages))
            
    elif action == "Reorder Pages":
        reorder_input = st.text_input("Pages Range/Order", value="1", help="Contoh: 1, 3-5, even, odd, reverse, last")
        st.caption("Pages Example: 1, 3-5, even, odd, reverse, last")
        
    elif action == "Delete Pages":
        delete_input = st.text_input("Pages to Delete", value="1", help="Contoh: 1, 3-5, even, odd, last")
        st.caption("Pages Example: 1, 3-5, even, odd, last")

    st.divider()

    # 2. Opsi Pengaturan Tambahan (Checkboxes)
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        keep_bookmarks = st.checkbox("Keep Bookmarks", value=False)
        extract_separate = st.checkbox("Extract Pages As Separate Files", value=False)
    with col_opt2:
        save_other_pages = st.checkbox("Save the other pages as a PDF file", value=False)

    st.divider()

    # 3. Form Proses & Download
    output_filename = st.text_input("Nama File Output:", value=f"processed_{uploaded_file.name}")
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"

    if st.button("🚀 Process & Save As...", type="primary"):
        try:
            # Tentukan urutan halaman yang akan diproses
            if action == "Split Pages From":
                target_pages = list(range(int(from_page), int(to_page) + 1))
            elif action == "Reorder Pages":
                target_pages = parse_page_range(reorder_input, total_pages)
            elif action == "Delete Pages":
                pages_to_delete = set(parse_page_range(delete_input, total_pages))
                target_pages = [p for p in range(1, total_pages + 1) if p not in pages_to_delete]

            if not target_pages:
                st.error("Rentang halaman tidak valid atau tidak ada halaman yang diproses!")
                st.stop()

            # Mode Pemisahan File Terpisah
            if extract_separate and len(target_pages) > 1:
                zip_buffer = io.BytesIO()
                import zipfile
                
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for page_num in target_pages:
                        writer = PdfWriter()
                        writer.add_page(reader.pages[page_num - 1])
                        
                        pdf_bytes = io.BytesIO()
                        writer.write(pdf_bytes)
                        pdf_bytes.seek(0)
                        
                        zip_file.writestr(f"page_{page_num}.pdf", pdf_bytes.getvalue())
                
                zip_buffer.seek(0)
                st.success("File PDF berhasil dipisah per halaman!")
                st.download_button(
                    label="📥 Download ZIP All Extracted Pages",
                    data=zip_buffer,
                    file_name="extracted_pages.zip",
                    mime="application/zip"
                )
            
            # Mode Penggabungan Utama
            else:
                writer = PdfWriter()
                for page_num in target_pages:
                    writer.add_page(reader.pages[page_num - 1])
                
                # Simpan Bookmarks jika diisi
                if keep_bookmarks and hasattr(reader, "outline") and reader.outline:
                    try:
                        writer.clone_outline_from(reader)
                    except Exception:
                        pass

                pdf_buffer = io.BytesIO()
                writer.write(pdf_buffer)
                pdf_buffer.seek(0)

                st.success("Proses PDF berhasil!")
                st.download_button(
                    label="📥 Download Processed PDF",
                    data=pdf_buffer,
                    file_name=output_filename,
                    mime="application/pdf"
                )

                # Jika opsi 'Save the other pages as a PDF file' dicentang
                if save_other_pages:
                    other_pages = [p for p in range(1, total_pages + 1) if p not in target_pages]
                    if other_pages:
                        other_writer = PdfWriter()
                        for p_num in other_pages:
                            other_writer.add_page(reader.pages[p_num - 1])
                        
                        other_buffer = io.BytesIO()
                        other_writer.write(other_buffer)
                        other_buffer.seek(0)

                        st.download_button(
                            label="📥 Download Other Pages (Sisa Halaman)",
                            data=other_buffer,
                            file_name=f"remaining_{output_filename}",
                            mime="application/pdf"
                        )

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses PDF: {e}")

import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Edit Tanda Tangan SPBY (Multi-Halaman Presisi)")

uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    st.subheader("⚙️ Pengaturan Posisi & Jarak Spasi TTE")
    y_offset_tte = st.slider(
        "Jarak Teks TTE dari Atas (Offset Y)", 
        min_value=0, 
        max_value=40, 
        value=20, 
        help="Geser untuk mengatur spasi vertikal teks TTE, Nama, dan NIP"
    )

    col1, col2 = st.columns(2)
    with col1:
        add_tte_bendahara = st.checkbox("Tambah TTE Bendahara Pengeluaran (Hal 1)", value=True)
        bendahara_nama = st.text_input("Nama Bendahara", value="DENDY ISYANDI ALWIYUDIN")
        bendahara_nip = st.text_input("NIP Bendahara", value="NIP 199603302018121002")

    with col2:
        add_tte_ppk = st.checkbox("Tambah TTE Pejabat Pembuat Komitmen", value=True)
        ppk_nama = st.text_input("Nama PPK", value="DEVRI OSKANDAR")
        ppk_nip = st.text_input("NIP PPK", value="NIP 197712082000121001")

    if st.button("🔄 Diproses & Aplikasikan TTE"):
        with st.spinner("Memproses dokumen SPBY..."):
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect

                # Deteksi lokasi PPK / Bendahara di halaman saat ini
                rects_ppk = page.search_for(ppk_nama)
                rects_bend = page.search_for(bendahara_nama)
                rects_penerima = page.search_for("Penerima Uang")

                if rects_ppk or rects_bend:
                    # ==========================================
                    # HALAMAN 1 (Ada Kotak + Penerima Uang + Footer)
                    # ==========================================
                    if page_num == 0:
                        y_start = rects_bend[0].y0 if rects_bend else 700
                        x_bend = rects_bend[0].x0 if rects_bend else 35
                        x_ppk = rects_ppk[0].x0 if rects_ppk else 380
                        x_penerima = rects_penerima[0].x0 if rects_penerima else 210

                        margin_left = 18.0
                        margin_right = page_rect.x1 - 18.0

                        # Hapus area bawah
                        clear_rect = fitz.Rect(margin_left + 0.5, y_start - 12, margin_right - 0.5, page_rect.y1 - 5)
                        page.add_redact_annot(clear_rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        y_curr = y_start + y_offset_tte

                        # Tulis Bendahara
                        if add_tte_bendahara:
                            page.insert_text(fitz.Point(x_bend, y_curr - 12), "Ditandatangani secara elektronik", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
                        page.insert_text(fitz.Point(x_bend, y_curr), bendahara_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                        page.insert_text(fitz.Point(x_bend, y_curr + 12), bendahara_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                        # Tulis Titik-titik Penerima Uang
                        page.insert_text(fitz.Point(x_penerima, y_curr - 2), "...................................................", fontsize=8, fontname="helv", color=(0, 0, 0))
                        page.insert_text(fitz.Point(x_penerima, y_curr + 12), "...................................................", fontsize=8, fontname="helv", color=(0, 0, 0))

                        # Tulis PPK
                        if add_tte_ppk:
                            page.insert_text(fitz.Point(x_ppk, y_curr - 12), "Ditandatangani secara elektronik", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
                        page.insert_text(fitz.Point(x_ppk, y_curr), ppk_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                        page.insert_text(fitz.Point(x_ppk, y_curr + 12), ppk_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                        # Dicetak pada tanggal khusus Halaman 1
                        y_dicetak = y_curr + 24
                        page.insert_text(fitz.Point(x_ppk + 30, y_dicetak), "Dicetak pada tanggal 22 Oktober 2026", fontsize=7.5, fontname="helv", color=(0, 0, 0))

                        # Bingkai Halaman 1
                        line_y_start = y_start - 12.5
                        new_bottom_y = y_dicetak + 8
                        page.draw_line(fitz.Point(margin_left, line_y_start), fitz.Point(margin_left, new_bottom_y), color=(0, 0, 0), width=1.0)
                        page.draw_line(fitz.Point(margin_right, line_y_start), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)
                        page.draw_line(fitz.Point(margin_left, new_bottom_y), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)

                    # ==========================================
                    # HALAMAN 2 (Pakai Kotak + Tanpa "Dicetak pada...")
                    # ==========================================
                    elif page_num == 1:
                        y_start = rects_ppk[0].y0 if rects_ppk else 700
                        x_ppk = rects_ppk[0].x0 if rects_ppk else 380

                        margin_left = 18.0
                        margin_right = page_rect.x1 - 18.0

                        # Hapus area nama lama & footer jika ada
                        clear_rect = fitz.Rect(margin_left + 0.5, y_start - 12, margin_right - 0.5, page_rect.y1 - 5)
                        page.add_redact_annot(clear_rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        y_curr = y_start + y_offset_tte

                        # Tulis PPK dengan TTE
                        if add_tte_ppk:
                            page.insert_text(fitz.Point(x_ppk, y_curr - 12), "Ditandatangani secara elektronik", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
                        page.insert_text(fitz.Point(x_ppk, y_curr), ppk_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                        page.insert_text(fitz.Point(x_ppk, y_curr + 12), ppk_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                        # Gambar Kotak Bingkai Bawah (Tanpa Teks Dicetak pada...)
                        line_y_start = y_start - 12.5
                        new_bottom_y = y_curr + 22
                        page.draw_line(fitz.Point(margin_left, line_y_start), fitz.Point(margin_left, new_bottom_y), color=(0, 0, 0), width=1.0)
                        page.draw_line(fitz.Point(margin_right, line_y_start), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)
                        page.draw_line(fitz.Point(margin_left, new_bottom_y), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)

                    # ==========================================
                    # HALAMAN 3 DUSTA / KETIGA (TANPA Kotak + TANPA "Dicetak pada...")
                    # ==========================================
                    else:
                        y_start = rects_ppk[0].y0 if rects_ppk else 700
                        x_ppk = rects_ppk[0].x0 if rects_ppk else 380

                        # Hapus hanya area nama & NIP lama
                        clear_rect = fitz.Rect(x_ppk - 10, y_start - 12, page_rect.x1 - 10, page_rect.y1 - 5)
                        page.add_redact_annot(clear_rect, fill=(1, 1, 1))
                        page.apply_redactions()

                        y_curr = y_start + y_offset_tte

                        # Tulis PPK dengan TTE
                        if add_tte_ppk:
                            page.insert_text(fitz.Point(x_ppk, y_curr - 12), "Ditandatangani secara elektronik", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
                        page.insert_text(fitz.Point(x_ppk, y_curr), ppk_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                        page.insert_text(fitz.Point(x_ppk, y_curr + 12), ppk_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))
                        
                        # (Halaman 3 murni tanpa drawing garis & tanpa teks dicetak)

            output_bytes = doc.tobytes()
            doc.close()

            st.success("Format Halaman 1, 2, dan 3 berhasil disesuaikan!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Final.pdf",
                mime="application/pdf"
            )

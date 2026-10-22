import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Tambah Tanda Tangan Elektronik SPBY (Otomatis)")

uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    # Nilai Offset Y diset otomatis (presisi = 40)
    Y_OFFSET_TTE = 40

    col1, col2 = st.columns(2)
    with col1:
        add_tte_bendahara = st.checkbox("Tambah TTE Bendahara Pengeluaran", value=True)
        bendahara_nama = st.text_input("Nama Bendahara", value="DENDY ISYANDI ALWIYUDIN")
        bendahara_nip = st.text_input("NIP Bendahara", value="NIP 199603302018121002")

    with col2:
        add_tte_ppk = st.checkbox("Tambah TTE Pejabat Pembuat Komitmen", value=True)
        ppk_nama = st.text_input("Nama PPK", value="DEVRI OSKANDAR")
        ppk_nip = st.text_input("NIP PPK", value="NIP 197712082000121001")

    if st.button("🔄 Diproses & Tambahkan TTE Otomatis"):
        with st.spinner("Memproses penyuntingan seluruh halaman PDF..."):
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            # Iterasi ke seluruh halaman PDF
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect

                # 1. Cari lokasi acuan teks di halaman saat ini
                rects_bend = page.search_for(bendahara_nama)
                rects_ppk = page.search_for(ppk_nama)
                rects_penerima = page.search_for("Penerima Uang")

                if rects_ppk or rects_bend:
                    y_start = rects_bend[0].y0 if rects_bend else (rects_ppk[0].y0 if rects_ppk else 700)
                    x_bend = rects_bend[0].x0 if rects_bend else 35
                    x_ppk = rects_ppk[0].x0 if rects_ppk else 380
                    x_penerima = rects_penerima[0].x0 if rects_penerima else 210

                    margin_left = 18.0
                    margin_right = page_rect.x1 - 18.0

                    # 2. HAPUS BERSIH seluruh area bawah dari y_start sampai batas halaman
                    clear_rect = fitz.Rect(
                        margin_left + 0.5, 
                        y_start - 12, 
                        margin_right - 0.5, 
                        page_rect.y1 - 5
                    )
                    page.add_redact_annot(clear_rect, fill=(1, 1, 1))
                    page.apply_redactions()

                    # 3. TULIS TEKS BARU (TTE, Nama, NIP, & Titik-titik Penerima Uang)
                    y_curr = y_start + Y_OFFSET_TTE

                    # --- KOLOM BENDAHARA ---
                    if rects_bend:
                        if add_tte_bendahara:
                            page.insert_text(
                                fitz.Point(x_bend, y_curr - 12),
                                "Ditandatangani secara elektronik",
                                fontsize=8,
                                fontname="helv",
                                color=(0.4, 0.4, 0.4)
                            )
                        page.insert_text(
                            fitz.Point(x_bend, y_curr),
                            bendahara_nama,
                            fontsize=9,
                            fontname="helv",
                            color=(0, 0, 0)
                        )
                        page.insert_text(
                            fitz.Point(x_bend, y_curr + 12),
                            bendahara_nip,
                            fontsize=8.5,
                            fontname="helv",
                            color=(0, 0, 0)
                        )

                    # --- KOLOM PENERIMA UANG ---
                    if rects_penerima:
                        page.insert_text(
                            fitz.Point(x_penerima, y_curr - 2),
                            "...................................................",
                            fontsize=8,
                            fontname="helv",
                            color=(0, 0, 0)
                        )
                        page.insert_text(
                            fitz.Point(x_penerima, y_curr + 12),
                            "...................................................",
                            fontsize=8,
                            fontname="helv",
                            color=(0, 0, 0)
                        )

                    # --- KOLOM PPK ---
                    if rects_ppk:
                        if add_tte_ppk:
                            page.insert_text(
                                fitz.Point(x_ppk, y_curr - 12),
                                "Ditandatangani secara elektronik",
                                fontsize=8,
                                fontname="helv",
                                color=(0.4, 0.4, 0.4)
                            )
                        page.insert_text(
                            fitz.Point(x_ppk, y_curr),
                            ppk_nama,
                            fontsize=9,
                            fontname="helv",
                            color=(0, 0, 0)
                        )
                        page.insert_text(
                            fitz.Point(x_ppk, y_curr + 12),
                            ppk_nip,
                            fontsize=8.5,
                            fontname="helv",
                            color=(0, 0, 0)
                        )

                    # --- FOOTER DICETAK PADA TANGGAL ---
                    y_dicetak = y_curr + 24
                    page.insert_text(
                        fitz.Point(x_ppk + 30, y_dicetak),
                        "Dicetak pada tanggal 22 Oktober 2026",
                        fontsize=7.5,
                        fontname="helv",
                        color=(0, 0, 0)
                    )

                    # 4. SAMBUNGKAN BINGKAI LUAR SECARA PRESISI
                    line_y_start = y_start - 12.5
                    new_bottom_y = y_dicetak + 8

                    page.draw_line(
                        fitz.Point(margin_left, line_y_start),
                        fitz.Point(margin_left, new_bottom_y),
                        color=(0, 0, 0),
                        width=1.0
                    )
                    page.draw_line(
                        fitz.Point(margin_right, line_y_start),
                        fitz.Point(margin_right, new_bottom_y),
                        color=(0, 0, 0),
                        width=1.0
                    )
                    page.draw_line(
                        fitz.Point(margin_left, new_bottom_y),
                        fitz.Point(margin_right, new_bottom_y),
                        color=(0, 0, 0),
                        width=1.0
                    )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("TTE berhasil diproses otomatis untuk semua halaman!")
            st.download_button(
                label="📥 Download PDF SPBY TTE",
                data=output_bytes,
                file_name="SPBY_TTE_Otomatis.pdf",
                mime="application/pdf"
            )

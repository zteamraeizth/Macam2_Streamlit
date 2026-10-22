import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Batch Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Batch Tambah TTE SPBY (Fix Garis Halaman 2)")

uploaded_files = st.file_uploader("Upload File PDF SPBY", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    Y_OFFSET_TTE = 40

    st.subheader("⚙️ Pengaturan Pejabat Penandatangan")
    col1, col2 = st.columns(2)
    with col1:
        add_tte_bendahara = st.checkbox("Tambah TTE Bendahara Pengeluaran", value=True)
        bendahara_nama = st.text_input("Nama Bendahara", value="DENDY ISYANDI ALWIYUDIN")
        bendahara_nip = st.text_input("NIP Bendahara", value="NIP 199603302018121002")

    with col2:
        add_tte_ppk = st.checkbox("Tambah TTE Pejabat Pembuat Komitmen", value=True)
        ppk_nama = st.text_input("Nama PPK", value="DEVRI OSKANDAR")
        ppk_nip = st.text_input("NIP PPK", value="NIP 197712082000121001")

    if st.button("🔄 Diproses Semua File"):
        processed_files = []
        merged_doc = fitz.open()

        with st.spinner("Memproses seluruh file PDF..."):
            for pdf_file in uploaded_files:
                pdf_bytes = pdf_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    page_rect = page.rect

                    rects_bend = page.search_for(bendahara_nama)
                    rects_ppk = page.search_for(ppk_nama)
                    rects_penerima = page.search_for("Penerima Uang")

                    margin_left = 18.0
                    margin_right = page_rect.x1 - 18.0

                    # -------------------------------------------------------------
                    # HALAMAN 1 (SPBY Utuh dengan Bingkai & Footer)
                    # -------------------------------------------------------------
                    if page_num == 0:
                        if rects_ppk or rects_bend:
                            y_start = rects_bend[0].y0 if rects_bend else (rects_ppk[0].y0 if rects_ppk else 700)
                            x_bend = rects_bend[0].x0 if rects_bend else 35
                            x_ppk = rects_ppk[0].x0 if rects_ppk else 380
                            x_penerima = rects_penerima[0].x0 if rects_penerima else 210

                            clear_rect = fitz.Rect(
                                margin_left + 0.5, 
                                y_start - 12, 
                                margin_right - 0.5, 
                                page_rect.y1 - 5
                            )
                            page.add_redact_annot(clear_rect, fill=(1, 1, 1))
                            page.apply_redactions()

                            y_curr = y_start + Y_OFFSET_TTE

                            if rects_bend:
                                if add_tte_bendahara:
                                    page.insert_text(
                                        fitz.Point(x_bend, y_curr - 12),
                                        "Ditandatangani secara elektronik",
                                        fontsize=8,
                                        fontname="helv",
                                        color=(0.4, 0.4, 0.4)
                                    )
                                page.insert_text(fitz.Point(x_bend, y_curr), bendahara_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                                page.insert_text(fitz.Point(x_bend, y_curr + 12), bendahara_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                            if rects_penerima:
                                page.insert_text(fitz.Point(x_penerima, y_curr - 2), "...................................................", fontsize=8, fontname="helv", color=(0, 0, 0))
                                page.insert_text(fitz.Point(x_penerima, y_curr + 12), "...................................................", fontsize=8, fontname="helv", color=(0, 0, 0))

                            if rects_ppk:
                                if add_tte_ppk:
                                    page.insert_text(
                                        fitz.Point(x_ppk, y_curr - 12),
                                        "Ditandatangani secara elektronik",
                                        fontsize=8,
                                        fontname="helv",
                                        color=(0.4, 0.4, 0.4)
                                    )
                                page.insert_text(fitz.Point(x_ppk, y_curr), ppk_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                                page.insert_text(fitz.Point(x_ppk, y_curr + 12), ppk_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                            y_dicetak = y_curr + 24
                            page.insert_text(fitz.Point(x_ppk + 30, y_dicetak), "Dicetak pada tanggal 22 Oktober 2026", fontsize=7.5, fontname="helv", color=(0, 0, 0))

                            line_y_start = y_start - 12.5
                            new_bottom_y = y_dicetak + 8
                            page.draw_line(fitz.Point(margin_left, line_y_start), fitz.Point(margin_left, new_bottom_y), color=(0, 0, 0), width=1.0)
                            page.draw_line(fitz.Point(margin_right, line_y_start), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)
                            page.draw_line(fitz.Point(margin_left, new_bottom_y), fitz.Point(margin_right, new_bottom_y), color=(0, 0, 0), width=1.0)

                    # -------------------------------------------------------------
                    # HALAMAN 2, 3, dst. (Redaction Aman Garis)
                    # -------------------------------------------------------------
                    else:
                        if rects_ppk:
                            for r in rects_ppk:
                                y_base = r.y0
                                
                                # A. Redact area teks presisi (dikunci sebelum margin_right agar garis tidak terpotong)
                                erase_rect = fitz.Rect(r.x0 - 45, y_base - 10, margin_right - 2, y_base + 35)
                                page.add_redact_annot(erase_rect, fill=(1, 1, 1))
                                page.apply_redactions()

                                x_pos = r.x0
                                y_curr = y_base + Y_OFFSET_TTE

                                # B. Tulis TTE di atas nama
                                if add_tte_ppk:
                                    page.insert_text(
                                        fitz.Point(x_pos, y_curr - 12),
                                        "Ditandatangani secara elektronik",
                                        fontsize=8,
                                        fontname="helv",
                                        color=(0.4, 0.4, 0.4)
                                    )
                                page.insert_text(fitz.Point(x_pos, y_curr), ppk_nama, fontsize=9, fontname="helv", color=(0, 0, 0))
                                page.insert_text(fitz.Point(x_pos, y_curr + 12), ppk_nip, fontsize=8.5, fontname="helv", color=(0, 0, 0))

                                # C. Sambungkan garis vertikal kanan di Halaman 2 agar utuh menyambung
                                page.draw_line(
                                    fitz.Point(margin_right, y_base - 15),
                                    fitz.Point(margin_right, y_curr + 25),
                                    color=(0, 0, 0),
                                    width=1.0
                                )

                out_bytes = doc.tobytes()
                new_filename = f"TTE_{pdf_file.name}"
                processed_files.append((new_filename, out_bytes))

                merged_doc.insert_pdf(doc)
                doc.close()

            merged_bytes = merged_doc.tobytes()
            merged_doc.close()

            st.session_state["processed_files"] = processed_files
            st.session_state["merged_bytes"] = merged_bytes
            st.success("Garis di Halaman 2 berhasil tersambung utuh!")

    # Opsi Download
    if "processed_files" in st.session_state and st.session_state["processed_files"]:
        st.write("---")
        st.subheader("📥 Opsi Download PDF")

        st.download_button(
            label="📦 Download Semua PDF Gabungan (Merged PDF)",
            data=st.session_state["merged_bytes"],
            file_name="SPBY_TTE_Merged_Gabungan.pdf",
            mime="application/pdf",
            type="primary"
        )

        st.write("---")
        st.write("**Atau Download File Satu per Satu:**")

        for filename, b_data in st.session_state["processed_files"]:
            st.download_button(
                label=f"📄 Download {filename}",
                data=b_data,
                file_name=filename,
                mime="application/pdf",
                key=filename
            )

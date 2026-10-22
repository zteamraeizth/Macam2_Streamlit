import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Tambah Tanda Tangan Elektronik SPBY")

uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    st.subheader("⚙️ Pengaturan Posisi & Jarak Spasi TTE")
    # Slider ditukar max_value ke 50
    y_offset_tte = st.slider(
        "Jarak Teks TTE dari Atas (Offset Y)", 
        min_value=0, 
        max_value=50, 
        value=20, 
        help="Semakin besar nilainya, semakin turun posisi TTE, Nama, NIP, dan garis bawah"
    )

    col1, col2 = st.columns(2)
    with col1:
        add_tte_bendahara = st.checkbox("Tambah TTE Bendahara Pengeluaran", value=True)
        bendahara_nama = st.text_input("Nama Bendahara", value="DENDY ISYANDI ALWIYUDIN")
        bendahara_nip = st.text_input("NIP Bendahara", value="NIP 199603302018121002")

    with col2:
        add_tte_ppk = st.checkbox("Tambah TTE Pejabat Pembuat Komitmen", value=True)
        ppk_nama = st.text_input("Nama PPK", value="DEVRI OSKANDAR")
        ppk_nip = st.text_input("NIP PPK", value="NIP 197712082000121001")

    if st.button("🔄 Diproses & Tambahkan TTE"):
        with st.spinner("Memproses penyuntingan PDF..."):
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]

            # 1. Bersihkan dan turunkan footer "Dicetak pada tanggal..." agar tidak bertindih
            dicetak_rects = page.search_for("Dicetak pada tanggal")
            dicetak_text = ""
            dicetak_x0 = 0
            dicetak_y0 = 0

            for d_rect in dicetak_rects:
                # Ambil seluruh baris teks footer
                full_line_rect = fitz.Rect(d_rect.x0 - 5, d_rect.y0 - 2, d_rect.x1 + 120, d_rect.y1 + 5)
                # Padam teks footer lama
                page.add_redact_annot(full_line_rect, fill=(1, 1, 1))
                dicetak_x0 = d_rect.x0
                dicetak_y0 = d_rect.y0

            # 2. Fungsi untuk menulis TTE, Nama, dan NIP
            def add_tte_text(target_name, target_nip, use_tte):
                rects = page.search_for(target_name)
                for rect in rects:
                    # Padam kawasan lama dari atas hingga ke bawah footer
                    clean_rect = fitz.Rect(
                        rect.x0 - 5, 
                        rect.y0 - 30, 
                        rect.x1 + 80, 
                        rect.y1 + 35
                    )
                    page.add_redact_annot(clean_rect, fill=(1, 1, 1))

                    x_pos = rect.x0
                    y_base = rect.y0 

                    # Tulis TTE
                    if use_tte:
                        page.insert_text(
                            fitz.Point(x_pos, y_base - 12 + y_offset_tte),
                            "Ditandatangani secara elektronik",
                            fontsize=8,
                            fontname="helv",
                            color=(0.4, 0.4, 0.4)
                        )

                    # Tulis Nama
                    page.insert_text(
                        fitz.Point(x_pos, y_base + y_offset_tte),
                        target_name,
                        fontsize=9,
                        fontname="helv",
                        color=(0, 0, 0)
                    )

                    # Tulis NIP
                    page.insert_text(
                        fitz.Point(x_pos, y_base + 12 + y_offset_tte),
                        target_nip,
                        fontsize=8.5,
                        fontname="helv",
                        color=(0, 0, 0)
                    )

            # 3. Jalankan pengemaskinian TTE
            add_tte_text(bendahara_nama, bendahara_nip, add_tte_bendahara)
            add_tte_text(ppk_nama, ppk_nip, add_tte_ppk)

            # Terapkan semua pemadaman (redactions)
            page.apply_redactions()

            # 4. Tulis semula footer "Dicetak pada tanggal..." di posisi lebih bawah
            if dicetak_x0 > 0:
                # Cari teks tanggal spesifik jika ada
                page.insert_text(
                    fitz.Point(dicetak_x0 - 10, dicetak_y0 + y_offset_tte + 8),
                    "Dicetak pada tanggal 22 Oktober 2026",
                    fontsize=7.5,
                    fontname="helv",
                    color=(0, 0, 0)
                )

            # 5. Turunkan garisan bingkai bawah (Bottom Border)
            # Cari garisan bingkai bawah asal dan padam
            page_rect = page.rect
            bottom_box = fitz.Rect(page_rect.x0, page_rect.y1 - 40, page_rect.x1, page_rect.y1)
            
            # Lukis garisan bingkai bawah baru disesuaikan dengan offset
            new_bottom_y = dicetak_y0 + y_offset_tte + 14
            page.draw_line(
                fitz.Point(30, new_bottom_y), 
                fitz.Point(page_rect.x1 - 30, new_bottom_y), 
                color=(0, 0, 0), 
                width=1
            )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("TTE dan garisan bawah berjaya disesuaikan tanpa bertindih!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

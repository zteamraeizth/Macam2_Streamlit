import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Tambah Tanda Tangan Elektronik SPBY")

uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    st.subheader("⚙️ Pengaturan Posisi & Jarak Spasi TTE")
    y_offset_tte = st.slider(
        "Jarak Teks TTE dari Atas (Offset Y)", 
        min_value=0, 
        max_value=60, 
        value=25, 
        help="Semakin besar nilainya, semakin turun posisi TTE, Nama, NIP, dan garis bingkai"
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
            page_rect = page.rect

            # 1. Cari lokasi acuan teks awal
            rects_bend = page.search_for(bendahara_nama)
            rects_ppk = page.search_for(ppk_nama)

            y_start = rects_bend[0].y0 if rects_bend else (rects_ppk[0].y0 if rects_ppk else 700)
            
            # Cari koordinat X asal dari teks Bendahara / PPK (diberi batas kiri aman agar tidak menempel garis)
            x_bend = rects_bend[0].x0 if rects_bend else 35
            x_ppk = rects_ppk[0].x0 if rects_ppk else 380

            # 2. Tentukan koordinat presisi garis bingkai luar (Margin standar SPBY KPP)
            # Koordinat garis luar kiri dan kanan standar dokumen SAKTI/Coretax SPBY
            margin_left = 18.0   # Tepat sejajar garis bingkai atas
            margin_right = page_rect.x1 - 18.0

            # 3. Hapus area bawah presisi di DALAM bingkai (tanpa merusak sambungan atas)
            clear_area = fitz.Rect(
                margin_left + 1,  # Hapus tepat di dalam garis
                y_start - 12,     # Tepat di bawah teks 'Bendahara Pengeluaran' & 'PPK'
                margin_right - 1,
                page_rect.y1 - 5
            )
            page.add_redact_annot(clear_area, fill=(1, 1, 1))
            page.apply_redactions()

            # 4. Tulis Teks Baru (TTE, Nama, NIP)
            y_curr = y_start + y_offset_tte

            # --- BENDAHARA ---
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

            # --- PPK ---
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

            # --- DICETAK PADA TANGGAL ---
            y_dicetak = y_curr + 26
            page.insert_text(
                fitz.Point(x_ppk + 30, y_dicetak),
                "Dicetak pada tanggal 22 Oktober 2026",
                fontsize=7.5,
                fontname="helv",
                color=(0, 0, 0)
            )

            # 5. Lukis Ulang Garis Bingkai (Sambungan Presisi)
            new_bottom_y = y_dicetak + 8

            # Garis Vertikal Kiri (Menyambung dari y_start ke bawah)
            page.draw_line(
                fitz.Point(margin_left, y_start - 12),
                fitz.Point(margin_left, new_bottom_y),
                color=(0, 0, 0),
                width=0.8
            )

            # Garis Vertikal Kanan
            page.draw_line(
                fitz.Point(margin_right, y_start - 12),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=0.8
            )

            # Garis Horizontal Bawah
            page.draw_line(
                fitz.Point(margin_left, new_bottom_y),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=0.8
            )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("Kotak bingkai berhasil dirapikan dan tersambung lurus!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

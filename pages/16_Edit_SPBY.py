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

            # 1. Cari titik acuan lokasi Bendahara dan PPK sebelum dibersihkan
            rects_bend = page.search_for(bendahara_nama)
            rects_ppk = page.search_for(ppk_nama)
            rects_dicetak = page.search_for("Dicetak pada tanggal")

            y_start = rects_bend[0].y0 if rects_bend else (rects_ppk[0].y0 if rects_ppk else 700)
            x_bend = rects_bend[0].x0 if rects_bend else 50
            x_ppk = rects_ppk[0].x0 if rects_ppk else 400

            # 2. HAPUS LENGKAP seluruh area bawah (termasuk garis border lama dan teks dicetak)
            # Menghapus seluruh bagian paling bawah halaman sampai batas pinggir
            clear_area = fitz.Rect(
                20,               # x0 dari garis kiri
                y_start - 10,     # y0 tepat di atas nama lama
                page_rect.x1 - 20,# x1 sampai garis kanan
                page_rect.y1 - 10 # y1 sampai bawah halaman
            )
            page.add_redact_annot(clear_area, fill=(1, 1, 1))
            page.apply_redactions()

            # 3. TULIS TEKS BARU (TTE, Nama, NIP)
            # --- BENDAHARA ---
            y_curr = y_start + y_offset_tte
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

            # 4. TULIS ULANG TEKS "Dicetak pada tanggal..." DI BAWAH NIP
            y_dicetak = y_curr + 26
            page.insert_text(
                fitz.Point(x_ppk + 30, y_dicetak),
                "Dicetak pada tanggal 22 Oktober 2026",
                fontsize=7.5,
                fontname="helv",
                color=(0, 0, 0)
            )

            # 5. LUKIS ULANG GARIS BINGKAI TABEL LENGKAP
            # Margin bingkai luar PDF SPBY SAKTI
            margin_left = 30
            margin_right = page_rect.x1 - 30
            new_bottom_y = y_dicetak + 8  # Posisi garis bawah persis di bawah teks dicetak

            # Garis Horizontal Bawah Baru
            page.draw_line(
                fitz.Point(margin_left, new_bottom_y),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=1
            )

            # Garis Vertikal Kiri & Kanan (Menutup kotak sampai ke bawah)
            page.draw_line(
                fitz.Point(margin_left, y_start - 10),
                fitz.Point(margin_left, new_bottom_y),
                color=(0, 0, 0),
                width=1
            )
            page.draw_line(
                fitz.Point(margin_right, y_start - 10),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=1
            )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("TTE, NIP, teks cetak, dan garis bingkai berhasil diturunkan dengan rapi!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

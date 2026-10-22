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
        max_value=40, 
        value=20, 
        help="Geser untuk mengatur spasi vertikal teks TTE, Nama, NIP, dan titik-titik Penerima Uang"
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
            rects_penerima = page.search_for("Penerima Uang")

            y_start = rects_bend[0].y0 if rects_bend else 700
            x_bend = rects_bend[0].x0 if rects_bend else 35
            x_ppk = rects_ppk[0].x0 if rects_ppk else 380
            x_penerima = rects_penerima[0].x0 if rects_penerima else 210

            # Margin luar garis bingkai resmi PDF SAKTI
            margin_left = 18.0
            margin_right = page_rect.x1 - 18.0

            # 2. HAPUS BERSIH seluruh area bawah dari y_start sampai dasar halaman
            # Ini memastikan titik-titik lama dan garis lama terhapus total tanpa tersisa
            clear_rect = fitz.Rect(
                margin_left + 0.5, 
                y_start - 12, 
                margin_right - 0.5, 
                page_rect.y1 - 5
            )
            page.add_redact_annot(clear_rect, fill=(1, 1, 1))
            page.apply_redactions()

            # 3. TULIS TEKS BARU (TTE, Nama, NIP, & Titik-titik Penerima Uang)
            y_curr = y_start + y_offset_tte

            # --- KOLOM BENDAHARA ---
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

            # --- KOLOM PENERIMA UANG (Selalu Sejajar Vertikal dengan Nama Dendy) ---
            # Baris 1: Sejajar persis dengan baseline Nama Dendy/Devri
            page.insert_text(
                fitz.Point(x_penerima, y_curr - 2),
                "...................................................",
                fontsize=8,
                fontname="helv",
                color=(0, 0, 0)
            )
            # Baris 2: Sejajar persis dengan baseline NIP
            page.insert_text(
                fitz.Point(x_penerima, y_curr + 12),
                "...................................................",
                fontsize=8,
                fontname="helv",
                color=(0, 0, 0)
            )

            # --- KOLOM PPK ---
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

            # 4. SAMBUNGKAN BINGKAI LOKAL DENGAN UJUNG GARIS ASLI
            # Menggunakan width=1.0 sesuai ketebalan garis standar SAKTI
            line_y_start = y_start - 12.5  # Titik temu ujung garis vertikal atas
            new_bottom_y = y_dicetak + 8    # Posisi penutup bawah

            # Garis Vertikal Kiri
            page.draw_line(
                fitz.Point(margin_left, line_y_start),
                fitz.Point(margin_left, new_bottom_y),
                color=(0, 0, 0),
                width=1.0
            )

            # Garis Vertikal Kanan
            page.draw_line(
                fitz.Point(margin_right, line_y_start),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=1.0
            )

            # Garis Horizontal Penutup Bawah
            page.draw_line(
                fitz.Point(margin_left, new_bottom_y),
                fitz.Point(margin_right, new_bottom_y),
                color=(0, 0, 0),
                width=1.0
            )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("Tata letak TTE, titik-titik Penerima Uang, dan ujung garis bingkai berhasil menyambung presisi!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

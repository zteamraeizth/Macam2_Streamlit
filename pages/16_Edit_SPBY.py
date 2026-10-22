import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit Tanda Tangan SPBY", layout="wide")
st.title("📄 Tambah Tanda Tangan Elektronik SPBY")

uploaded_file = st.file_uploader("Upload File PDF SPBY", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    # Pengaturan Spasi Vertikal
    st.subheader("⚙️ Pengaturan Posisi & Jarak Spasi TTE")
    y_offset_tte = st.slider(
        "Jarak Teks TTE dari Atas (Offset Y)", 
        min_value=0, 
        max_value=30, 
        value=15, 
        help="Makin besar nilainya, makin jauh jaraknya dari Jabatan (makin ke bawah)"
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

            def add_tte_text(target_name, target_nip, use_tte):
                # Cari koordinat posisi nama pejabat pada dokumen
                rects = page.search_for(target_name)
                for rect in rects:
                    # Ambil area sekitar nama dan NIP untuk dibersihkan (redact)
                    clean_rect = fitz.Rect(
                        rect.x0 - 2, 
                        rect.y0 - 25,  # Area pembersihan diperluas ke atas
                        rect.x1 + 60, 
                        rect.y1 + 15
                    )
                    
                    page.add_redact_annot(clean_rect, fill=(1, 1, 1))
                    page.apply_redactions()

                    x_pos = rect.x0
                    # Posisi dasar nama asli
                    y_base = rect.y0 

                    # Tulis TTE dengan mengatur jarak vertikal
                    if use_tte:
                        # y_offset_tte memberikan jarak lebih lega dari teks Jabatan di atasnya
                        page.insert_text(
                            fitz.Point(x_pos, y_base - 12 + y_offset_tte),
                            "Ditandatangani secara elektronik",
                            fontsize=8,
                            fontname="helv",
                            color=(0.4, 0.4, 0.4)  # Abu-abu
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

            # Eksekusi pembaruan TTE
            add_tte_text(bendahara_nama, bendahara_nip, add_tte_bendahara)
            add_tte_text(ppk_nama, ppk_nip, add_tte_ppk)

            output_bytes = doc.tobytes()
            doc.close()

            st.success("Teks TTE berhasil disesuaikan dengan jarak spasi baru!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

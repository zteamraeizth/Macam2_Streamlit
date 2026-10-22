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
        max_value=50, 
        value=20, 
        help="Geser untuk mengatur jarak turun teks TTE, Nama, dan NIP"
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

            # 1. Simpan koordinat awal nama pejabat SEBELUM ada pembersihan/redact
            pejabat_coords = []
            
            # Cari posisi Bendahara
            rects_bend = page.search_for(bendahara_nama)
            if rects_bend:
                pejabat_coords.append({
                    "name": bendahara_nama,
                    "nip": bendahara_nip,
                    "use_tte": add_tte_bendahara,
                    "rect": rects_bend[0]
                })

            # Cari posisi PPK
            rects_ppk = page.search_for(ppk_nama)
            if rects_ppk:
                pejabat_coords.append({
                    "name": ppk_nama,
                    "nip": ppk_nip,
                    "use_tte": add_tte_ppk,
                    "rect": rects_ppk[0]
                })

            # 2. Hapus HANYA area nama dan NIP lama (Presisi tanpa merusak garis border)
            for item in pejabat_coords:
                r = item["rect"]
                # Area hapus presisi setinggi teks nama + NIP (sekitar 30pt ke bawah)
                erase_rect = fitz.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 80, r.y1 + 25)
                page.add_redact_annot(erase_rect, fill=(1, 1, 1))

            # Eksekusi pembersihan teks lama
            page.apply_redactions()

            # 3. Tuliskan teks baru (TTE, Nama, NIP) di posisi yang disesuaikan offset Y
            for item in pejabat_coords:
                x_pos = item["rect"].x0
                y_base = item["rect"].y0

                # Tulis TTE
                if item["use_tte"]:
                    page.insert_text(
                        fitz.Point(x_pos, y_base - 10 + y_offset_tte),
                        "Ditandatangani secara elektronik",
                        fontsize=8,
                        fontname="helv",
                        color=(0.4, 0.4, 0.4)
                    )

                # Tulis Nama
                page.insert_text(
                    fitz.Point(x_pos, y_base + 3 + y_offset_tte),
                    item["name"],
                    fontsize=9,
                    fontname="helv",
                    color=(0, 0, 0)
                )

                # Tulis NIP
                page.insert_text(
                    fitz.Point(x_pos, y_base + 15 + y_offset_tte),
                    item["nip"],
                    fontsize=8.5,
                    fontname="helv",
                    color=(0, 0, 0)
                )

            output_bytes = doc.tobytes()
            doc.close()

            st.success("TTE berhasil ditambahkan dengan garis border tetap utuh!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_TTE_Edited.pdf",
                mime="application/pdf"
            )

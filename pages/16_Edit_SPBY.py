import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(page_title="Edit SPBY Presisi", layout="wide")
st.title("📄 Form Editor SPBY (Layout Utuh)")

uploaded_file = st.file_uploader("Upload File PDF SPBY Asli", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    # 1. Ekstrak Teks Awal untuk Nilai Default Input Form
    doc_init = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = doc_init[0].get_text() if len(doc_init) > 0 else ""
    doc_init.close()

    st.subheader("📝 Edit Field Dokumen SPBY")
    
    col1, col2 = st.columns(2)
    with col1:
        nomor = st.text_input("Nomor SPBY", value="00520/PB/410248/2026")
        tanggal = st.text_input("Tanggal SPBY", value="22 Oktober 2026")
        nominal_angka = st.text_input("Nominal (Rp)", value="Rp. 440.000,00")
        nominal_terbilang = st.text_input("Terbilang", value="Empat Ratus Empat Puluh Ribu Rupiah")
        kepada = st.text_input("Kepada", value="Happy Yess")
        mak = st.text_input("Kegiatan, Output, MAK", value="015.04.CC.4791.BMA.521211")

    with col2:
        untuk_pembayaran = st.text_area(
            "Untuk Pembayaran", 
            value="pembayaran belanja barang berupa pembelian 45 box snack rapat dalam rangka undangan Pembahasan SP2DK dan Pemeriksaan Wajib Pajak sesuai UND-727, UND-730, UND-731, UND-757, UND-760, UND-761, UND-766 pada Happy Yess",
            height=130
        )
        ppk_nama = st.text_input("Nama PPK", value="DEVRI OSKANDAR")
        bendahara_nama = st.text_input("Nama Bendahara", value="DENDY ISYANDI ALWIYUDIN")

    # 2. Proses Re-generating PDF dengan Menimpa Teks
    if st.button("🔄 Generasi PDF Baru (Layout Presisi)"):
        with st.spinner("Memproses penyuntingan PDF..."):
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]

            # Daftar penggantian teks: (Teks Lama yang dicari, Teks Baru)
            replacements = [
                ("00520/PB/410248/2026", nomor),
                ("Happy Yess", kepada),
                ("015.04.CC.4791.BMA.521211", mak),
                ("DEVRI OSKANDAR", ppk_nama),
                ("DENDY ISYANDI ALWIYUDIN", bendahara_nama)
            ]

            # Proses pencarian dan penimpaan posisi teks
            for old_txt, new_txt in replacements:
                rects = page.search_for(old_txt)
                for rect in rects:
                    # Hapus teks lama dengan menutupnya warna putih
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    page.apply_redactions()
                    
                    # Tulis teks baru di lokasi koordinat yang sama
                    page.insert_text(
                        rect.tl + fitz.Point(0, 8),  # Sesuaikan baseline
                        new_txt,
                        fontsize=9,
                        fontname="helv",
                        color=(0, 0, 0)
                    )

            # Simpan PDF ke buffer
            output_bytes = doc.tobytes()
            doc.close()

            st.success("PDF berhasil diperbarui tanpa merusak layout!")
            st.download_button(
                label="📥 Download PDF SPBY Hasil Edit",
                data=output_bytes,
                file_name="SPBY_Edited.pdf",
                mime="application/pdf"
            )

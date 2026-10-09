import io
import re
import pandas as pd
import pdfplumber
import streamlit as st


def parse_pdf_fa_detail(pdf_file):
    rows = []
    current_sub_item = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            i = 0
            while i < len(lines):
                line = lines[i]

                # 1. KOLOM 1: Tangkap Sub-Item (Contoh: "000090. Kursi Eselon III")
                # Mengambil dari awal baris sampai sebelum angka nominal Pagu
                sub_match = re.match(r"^(\d{6}\.\s*[^0-9]+)", line)
                if sub_match:
                    current_sub_item = sub_match.group(1).strip()

                # 2. Tangkap Blok Transaksi (Diawali Tanggal dd-mm-yyyy)
                elif re.match(r"^\d{2}-\d{2}-\d{4}", line):
                    vendor_name = ""
                    deskripsi = ""

                    # --- KOLOM 3: Tangkap Nama Vendor ---
                    # Gabungkan teks baris tanggal dan 1-2 baris setelahnya untuk menangkap blok vendor
                    block_text = line
                    if i + 1 < len(lines):
                        block_text += " " + lines[i + 1]
                    if i + 2 < len(lines):
                        block_text += " " + lines[i + 2]

                    # Pola Vendor: Berada di antara Kode 'EP-XXXXXXXXX' dan Kode Acak 4-5 Huruf di akhir (misal WBWN / B8HY2 / CTFAP)
                    vendor_match = re.search(
                        r"EP-[A-Z0-9]+\s+(.*?)\s+(?=[A-Z0-9]{4,5}\b|\d[\d\.,]*$)",
                        block_text,
                    )

                    if vendor_match:
                        vendor_name = vendor_match.group(1).strip()
                    else:
                        # Fallback jika pola EP- tidak terdeteksi utuh
                        cleaned = re.sub(
                            r"^\d{2}-\d{2}-\d{4}\s*", "", block_text
                        )
                        cleaned = re.sub(r"EP-[A-Z0-9]+\s*", "", cleaned)
                        # Buang kode acak 4 karakter di ujung
                        cleaned = re.sub(
                            r"\b[A-Z0-9]{4,5}\b.*$", "", cleaned
                        ).strip()
                        vendor_name = cleaned

                    # --- KOLOM 2: Tangkap Deskripsi Paket ---
                    # Deskripsi Paket selalu diawali kata 'Pengadaan...' atau berada 1-2 baris di bawah transaksi
                    for offset in [1, 2, 3]:
                        if i + offset < len(lines):
                            target_line = lines[i + offset]
                            if target_line.startswith(
                                "Pengadaan"
                            ) or re.search(r"Paket\s+\d+", target_line):
                                deskripsi = target_line.strip()
                                break

                    # Masukkan ke list dengan urutan Kolom 1, Kolom 2, Kolom 3
                    rows.append({
                        "Sub Item / Barang": current_sub_item,
                        "Uraian / Paket": deskripsi,
                        "Nama Vendor": vendor_name,
                    })

                i += 1

    return rows


# ==========================================
# STREAMLIT UI
# ==========================================
st.set_page_config(
    page_title="PDF Extractor - Detail FA Modal", layout="wide"
)

st.title("📄 PDF to Excel Extractor - Detail FA Belanja Modal")
st.write("Upload PDF Laporan SAKTI untuk mengekstrak data ke format Excel.")

uploaded_files = st.file_uploader(
    "Pilih file PDF Laporan", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Total file terunggah: {len(uploaded_files)} file")

    if st.button("Proses Seluruh PDF"):
        all_data = []
        progress_bar = st.progress(0)

        for idx, file in enumerate(uploaded_files):
            extracted = parse_pdf_fa_detail(file)
            all_data.extend(extracted)
            progress_bar.progress((idx + 1) / len(uploaded_files))

        if all_data:
            df = pd.DataFrame(all_data)
            st.success(
                f"Selesai! Berhasil mengolah {len(all_data)} baris data."
            )

            st.subheader("Preview Hasil Ekstraksi Data")
            st.dataframe(df, use_container_width=True)

            # Export Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(
                    writer, index=False, sheet_name="Detail_Belanja_Modal"
                )
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download File Excel (.xlsx)",
                data=excel_data,
                file_name="Hasil_Ekstraksi_FA_Detail_Modal.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning(
                "Tidak ada data yang terdeteksi pada file PDF yang diunggah."
            )
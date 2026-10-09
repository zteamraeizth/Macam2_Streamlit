import io
import re
import pandas as pd
import streamlit as st


def parse_text_to_data(raw_text):
    """Marse teks log kegiatan menjadi list of dictionary berstruktur."""
    lines = [
        line.strip() for line in raw_text.strip().split("\n") if line.strip()
    ]
    records = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Cari pola "Id Kegiatan: <hash_id>"
        if "Id Kegiatan:" in line or "ID Kegiatan:" in line:
            id_kegiatan = line.split(":")[-1].strip()

            # Ambil Judul Kegiatan (1 baris sebelum Id Kegiatan)
            kegiatan = lines[i - 1] if i - 1 >= 0 else "-"

            # Ambil Tanggal dan Status (1 dan 2 baris setelah Id Kegiatan)
            tanggal = lines[i + 1] if i + 1 < len(lines) else "-"
            status = lines[i + 2] if i + 2 < len(lines) else "-"

            records.append(
                {
                    "id kegiatan": id_kegiatan,
                    "kegiatan": kegiatan,
                    "tanggal": tanggal,
                    "status": status,
                }
            )

        i += 1

    return records


def to_excel_bytes(df):
    """Mengubah DataFrame pandas menjadi byte stream file Excel (.xlsx)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data Kegiatan")
    return output.getvalue()


# ================= STREAMLIT UI =================
st.set_page_config(page_title="Text to Excel Converter", layout="wide")

st.title("📊 Ekstraksi Teks Kegiatan ke Tabel Excel")
st.write(
    "Tempelkan teks log kegiatan untuk mengonversinya langsung menjadi **File Excel (.xlsx)**."
)

# Text Area Input
input_text = st.text_area(
    "Paste Teks Mentah di Sini:",
    height=250,
    placeholder="Kunjungan Lapangan kepada Wajib Pajak\nId Kegiatan: 4080ffef\n15 September 2026\nBelum Lengkap\n\nMenyampaikan Permohonan Info Saldo...\nId Kegiatan: cefd5a15\n11 September 2026\nBelum Lengkap",
)

if st.button("🚀 Konversi ke Excel", type="primary"):
    if not input_text.strip():
        st.warning("Harap masukkan teks terlebih dahulu!")
    else:
        parsed_data = parse_text_to_data(input_text)

        if parsed_data:
            df = pd.DataFrame(parsed_data)

            # Reorder kolom sesuai urutan permintaan
            df = df[["id kegiatan", "kegiatan", "tanggal", "status"]]

            st.subheader("📋 Preview Tabel Data")
            st.dataframe(df, use_container_width=True)

            # Generate File Excel (.xlsx)
            excel_data = to_excel_bytes(df)

            # Tombol Download Excel
            st.download_button(
                label="📥 Download File Excel (.xlsx)",
                data=excel_data,
                file_name="data_kegiatan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Tidak dapat mengekstrak data. Pastikan format teks memuat 'Id Kegiatan:'"
            )
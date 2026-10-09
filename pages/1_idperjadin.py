import io
import re
import pandas as pd
import streamlit as st


def parse_multi_data_kegiatan(raw_text):
    """Marse teks log kegiatan multi-row secara presisi."""
    lines = [
        line.strip() for line in raw_text.strip().split("\n") if line.strip()
    ]
    records = []

    # Indeks lokasi ditemukannya "Id Kegiatan:"
    id_indices = [
        i
        for i, line in enumerate(lines)
        if "Id Kegiatan:" in line or "ID Kegiatan:" in line
    ]

    for idx, i in enumerate(id_indices):
        # Tentukan rentang baris untuk 1 blok kegiatan
        start_idx = id_indices[idx - 1] + 1 if idx > 0 else 0

        # Baris tepat sebelum "Id Kegiatan:" adalah Nama Kegiatan
        nama_kegiatan = lines[i - 1] if i - 1 >= 0 else "-"

        # 1. ID Kegiatan
        id_kegiatan = lines[i].split(":")[-1].strip()

        # Tentukan batas akhir pencarian dalam blok ini
        end_idx = id_indices[idx + 1] - 1 if idx + 1 < len(id_indices) else len(lines)
        block_lines = lines[i:end_idx]
        block_text = " ".join(block_lines)

        # 2. Deskripsi Sub Kegiatan (mencari baris 'Pelaksanaan tugas...')
        sub_kegiatan = "-"
        for line in block_lines:
            if "pelaksanaan tugas" in line.lower() or "tugas dan fungsi" in line.lower():
                sub_kegiatan = line
                break

        # 3. Tanggal (Mulai & Selesai)
        tgl_mulai = ""
        tgl_selesai = ""
        tanggal_str = "-"

        for j, line in enumerate(block_lines):
            if "MULAI" in line.upper() and j + 1 < len(block_lines):
                tgl_mulai = block_lines[j + 1]
            if "SELESAI" in line.upper() and j + 1 < len(block_lines):
                tgl_selesai = block_lines[j + 1]

        if tgl_mulai and tgl_selesai:
            tanggal_str = (
                tgl_mulai if tgl_mulai == tgl_selesai else f"{tgl_mulai} s.d. {tgl_selesai}"
            )

        # 4. Nomor ST dan Angka ST
        nomor_st = "-"
        no_st_num = "-"
        match_st = re.search(r"ST-\d+/[A-Z0-9.]+/\d{4}", block_text, re.IGNORECASE)
        if match_st:
            nomor_st = match_st.group(0)
            st_digits = re.search(r"ST-(\d+)", nomor_st, re.IGNORECASE)
            if st_digits:
                no_st_num = st_digits.group(1)

        records.append(
            {
                "No ST": no_st_num,
                "ID Kegiatan": id_kegiatan,
                "Deskripsi Sub Kegiatan": sub_kegiatan,
                "Status": "",  # Kolom status dikosongkan sesuai instruksi
                "Kode": "763",
                "Jenis SPD": "SPD Dalam Kota",
                "Nama Kegiatan": nama_kegiatan,
                "Tanggal": tanggal_str,
                "Nomor Surat Tugas": nomor_st,
            }
        )

    return records


def to_excel_bytes(df):
    """Konversi DataFrame ke file Excel (.xlsx) di dalam memori."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data Kegiatan")
    return output.getvalue()


# ================= STREAMLIT UI =================
st.set_page_config(page_title="Extractor Data Kegiatan", layout="wide")

st.title("⚡ Mass Extractor Data Kegiatan ke Excel")
st.write(
    "Mengekstrak ratusan data kegiatan secara presisi ke dalam format file Excel (.xlsx)."
)

input_text = st.text_area(
    "Paste Teks Mentah di Sini:",
    height=350,
    placeholder="""Surat Tugas Pengiriman Dossier Pegawai Mutasi Keluar KPP Pratama Jakarta Duren Sawit
Id Kegiatan: f35bccb4
MULAI
24 Juni 2026
SELESAI
24 Juni 2026
ST-391/KPP.2009/2026
Ndid: 64888528
Pelaksanaan tugas dan fungsi yang melekat pada jabatan (luar kota)
Kegiatan Disetujui
Kegiatan Pengamatan, KPD dan advisory visit Wajib Pajak
Id Kegiatan: a1fdb3fe
MULAI
11 Juni 2026
SELESAI
13 Juni 2026
ST-345/KPP.2009/2026
Ndid: 64613690
Pelaksanaan tugas dan fungsi yang melekat pada jabatan (dalam kota lebih dari 8 jam)
Kegiatan Disetujui""",
)

if st.button("🚀 Proses dan Generate Excel", type="primary"):
    if not input_text.strip():
        st.warning("Harap masukkan teks terlebih dahulu!")
    else:
        parsed_data = parse_multi_data_kegiatan(input_text)

        if parsed_data:
            df = pd.DataFrame(parsed_data)

            st.success(f"🎉 Berhasil mengekstrak **{len(df)} data kegiatan**!")

            st.subheader("📋 Tampilan Tabel Preview Data")
            st.dataframe(df, use_container_width=True)

            excel_bytes = to_excel_bytes(df)
            st.download_button(
                label=f"📥 Download File Excel ({len(df)} Data .xlsx)",
                data=excel_bytes,
                file_name="data_kegiatan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.error(
                "Gagal memproses data. Pastikan teks memuat 'Id Kegiatan:'"
            )
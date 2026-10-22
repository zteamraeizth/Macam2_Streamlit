import io
import re
import pandas as pd
import streamlit as st


def parse_multi_data_kegiatan(raw_text):
    """Marse teks log kegiatan multi-row secara presisi untuk format baru."""
    # Bersihkan baris kosong
    lines = [
        line.strip() for line in raw_text.strip().split("\n") if line.strip()
    ]
    records = []

    # Indeks baris yang memuat 'ID Kegiatan' atau 'Id Kegiatan'
    id_indices = [
        idx
        for idx, line in enumerate(lines)
        if re.search(r"ID\s*Kegiatan\s*:", line, re.IGNORECASE)
    ]

    for idx, i in enumerate(id_indices):
        # 1. Nama Kegiatan & ID Kegiatan
        line_id = lines[i]

        # Ambil Nama Kegiatan dari teks sebelum 'ID Kegiatan'
        # Jika 'ID Kegiatan' ada di baris tersendiri, ambil baris i-1
        # Jika 'ID Kegiatan' menempel di akhir baris nama kegiatan, pisahkan
        match_id = re.search(
            r"(.*?)(ID\s*Kegiatan\s*:\s*([a-f0-9]+))", line_id, re.IGNORECASE
        )

        if match_id:
            prefix_text = match_id.group(1).strip()
            id_kegiatan = match_id.group(3).strip()
            if prefix_text:
                nama_kegiatan = prefix_text
            else:
                nama_kegiatan = lines[i - 1] if i - 1 >= 0 else "-"
        else:
            id_kegiatan = line_id.split(":")[-1].strip()
            nama_kegiatan = lines[i - 1] if i - 1 >= 0 else "-"

        # Tentukan rentang blok baris untuk kegiatan ini
        end_idx = (
            id_indices[idx + 1] if idx + 1 < len(id_indices) else len(lines)
        )

        # Baris setelah ID Kegiatan
        next_line_idx = i + 1
        if (
            match_id
            and not match_id.group(1)
            and i - 1 >= 0
            and lines[i - 1] == nama_kegiatan
        ):
            # Jika nama kegiatan diambil dari i-1, blok data selanjutnya dari i+1
            pass

        remaining_lines = lines[next_line_idx:end_idx]
        block_text = " ".join(remaining_lines)

        # 2. Extract Nomor Surat Tugas (ST)
        nomor_st = "-"
        no_st_num = "-"
        match_st = re.search(
            r"ST-\d+/[A-Z0-9.]+/\d{4}", block_text, re.IGNORECASE
        )
        if match_st:
            nomor_st = match_st.group(0)
            st_digits = re.search(r"ST-(\d+)", nomor_st, re.IGNORECASE)
            if st_digits:
                no_st_num = st_digits.group(1)

        # 3. Extract Tanggal
        # Mencari pola tanggal Indonesia, contoh: "1 Oktober 2026" atau "24 September 2026"
        tanggal_str = "-"
        match_tgl = re.search(
            r"(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})",
            block_text,
            re.IGNORECASE,
        )
        if match_tgl:
            tanggal_str = match_tgl.group(1).strip()

        # 4. Extract Deskripsi Sub Kegiatan (jika ada)
        sub_kegiatan = "-"
        for line in remaining_lines:
            if (
                "pelaksanaan tugas" in line.lower()
                or "tugas dan fungsi" in line.lower()
            ):
                sub_kegiatan = line
                break

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
    placeholder="""Melaksanakan kegiatan penggalian potensi dan visit Wajib pajak serta kegiatan pengumpulan data lapangan (KPDL) dalam rangka pengamanan penerimaan Pajak Tahun 2026ID Kegiatan : 6ac35fd7836a92acbc36086c
1 Oktober 2026Belum ada laporanST-701/KPP.2009/2026

Monitoring Pelaksanaan Anggaran Triwulan III dan Bimtek ePerjadin Versi 2 Satuan Kerja Lingkup Kanwil DJP Jakarta Timur.ID Kegiatan : 6abccc0da4195d802b9be2d3
24 September 2026Laporan Tersedia
ST-668/KPP.2009/2026""",
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
                "Gagal memproses data. Pastikan teks memuat 'ID Kegiatan :'"
            )

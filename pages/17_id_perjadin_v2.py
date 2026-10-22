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

    # Cari semua baris yang memuat "ID Kegiatan"
    id_indices = [
        idx
        for idx, line in enumerate(lines)
        if re.search(r"ID\s*Kegiatan\s*:", line, re.IGNORECASE)
    ]

    for idx, i in enumerate(id_indices):
        # 1. Extract ID Kegiatan
        id_kegiatan = lines[i].split(":")[-1].strip()

        # Rentang baris untuk 1 blok kegiatan ini
        end_idx = (
            id_indices[idx + 1] if idx + 1 < len(id_indices) else len(lines)
        )
        block_lines = lines[i + 1 : end_idx]
        block_text = " ".join(block_lines)

        # 2. Nama Kegiatan (Baris pertama tepat setelah ID Kegiatan)
        nama_kegiatan = "-"
        if block_lines:
            nama_kegiatan = block_lines[0]

        # 3. Deskripsi Sub Kegiatan & Status Kegiatan
        sub_kegiatan = "-"
        status_kegiatan = "-"

        for line in block_lines:
            if (
                "pelaksanaan tugas" in line.lower()
                or "tugas dan fungsi" in line.lower()
            ):
                # Cari kata kunci status di akhir baris (misal: 'Disetujui' atau 'Baru Diusulkan')
                match_status = re.search(
                    r"(Disetujui|Baru Diusulkan|Kegiatan Disetujui)$",
                    line,
                    re.IGNORECASE,
                )
                if match_status:
                    status_kegiatan = match_status.group(1).strip()
                    # Bersihkan teks status dari baris deskripsi sub kegiatan
                    sub_kegiatan = re.sub(
                        r"(Disetujui|Baru Diusulkan|Kegiatan Disetujui)$",
                        "",
                        line,
                        flags=re.IGNORECASE,
                    ).strip()
                else:
                    sub_kegiatan = line.strip()
                break

        # Fallback pencarian status jika tidak berada di baris sub kegiatan
        if status_kegiatan == "-":
            for line in block_lines:
                if line.strip() in [
                    "Disetujui",
                    "Baru Diusulkan",
                    "Kegiatan Disetujui",
                ]:
                    status_kegiatan = line.strip()
                    break

        # 4. Tanggal (Mencari format tanggal Indonesia, contoh "20 Oktober 2026")
        tanggal_str = "-"
        match_tgl = re.search(
            r"(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})",
            block_text,
            re.IGNORECASE,
        )
        if match_tgl:
            tanggal_str = match_tgl.group(1).strip()

        # 5. Nomor Surat Tugas (ST)
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

        records.append(
            {
                "No ST": no_st_num,
                "ID Kegiatan": id_kegiatan,
                "Deskripsi Sub Kegiatan": sub_kegiatan,
                "Status": "",  # Dikosongkan sesuai instruksi sebelumnya
                "Status Kegiatan": status_kegiatan,  # Kolom Baru
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
    placeholder="""ID Kegiatan : 6ad8267b2b...
Advisory Visit dalam rangka tindak lanjut Surat Permintaan Penjelasan atas Data dan/atau Keterangan (SP2DK)
(Perjadin Rampung)
20 Oktober 2026ST-755/KPP.2009/2026NDID:68180834
Pelaksanaan tugas dan fungsi yang melekat pada jabatan (kurang dari hingga 8 jam)Disetujui""",
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

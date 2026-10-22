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
        # ID Kegiatan
        id_kegiatan = lines[i].split(":")[-1].strip()

        # Rentang baris untuk 1 blok kegiatan ini
        end_idx = (
            id_indices[idx + 1] if idx + 1 < len(id_indices) else len(lines)
        )
        block_lines = lines[i + 1 : end_idx]
        block_text = " ".join(block_lines)

        # 1. Nama Kegiatan (Baris pertama setelah ID Kegiatan)
        nama_kegiatan = "-"
        if block_lines:
            nama_kegiatan = block_lines[0]

        # 2. Deskripsi Sub Kegiatan (Mencari baris 'Pelaksanaan tugas...')
        sub_kegiatan = "-"
        for line in block_lines:
            if (
                "pelaksanaan tugas" in line.lower()
                or "tugas dan fungsi" in line.lower()
            ):
                # Bersihkan kata status jika menempel di akhir (misal: '...8 jam)Disetujui')
                sub_kegiatan = re.sub(
                    r"(Disetujui|Baru Diusulkan|Kegiatan Disetujui)$",
                    "",
                    line,
                    flags=re.IGNORECASE,
                ).strip()
                break

        # 3. Tanggal (Mencari format "20 Oktober 2026")
        tanggal_str = "-"
        match_tgl = re.search(
            r"(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s+\d{4})",
            block_text,
            re.IGNORECASE,
        )
        if match_tgl:
            tanggal_str = match_tgl.group(1).strip()

        # 4. Nomor Surat Tugas (ST)
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
                "Status": "",
                "Kode": "763",
                "Jenis SPD": "SPD Dalam Kota",
                "Nama Kegiatan": nama_kegiatan,
                "Tanggal": tanggal_str,
                "Nomor Surat Tugas": nomor_st,
            }
        )

    return records

import re
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(
    page_title="PDF to Excel Extractor Surat KPP", page_icon="📄", layout="wide"
)

st.title("📄 Extractor PDF Surat Undangan Pembahasan ke Excel")
st.write(
    "Unggah banyak file PDF (misal 10 file), aplikasi akan otomatis mengekstrak data ke format Excel."
)

# Pemetaan Nama AR ke Seksi Pengawasan
MAPPING_AR_SEKSI = {
    "Adhityarizka Rifadha": "Seksi Pengawasan III",
    "Agung Wirawan": "Seksi Pengawasan V",
    "Ahmad Arifuddin": "Seksi Pengawasan II",
    "Anindita Silvana": "Seksi Pengawasan IV",
    "Arief Yudha Kusuma": "Seksi Pengawasan I",
    "Atiek Yuni Indriani": "Seksi Pengawasan I",
    "Beni Tito Anggo": "Seksi Pengawasan I",
    "Chaterina Nainggolan": "Seksi Pengawasan II",
    "Dian Destinar": "Seksi Pengawasan I",
    "Dwi Hefriani": "Seksi Pengawasan VI",
    "Eko Susilo Hadi Ahmad": "Seksi Pengawasan VI",
    "Endah Sulistya Wardani": "Seksi Pengawasan V",
    "Fanny Rizky Aulia": "Seksi Pengawasan I",
    "Farkhan Abdillah": "Seksi Pengawasan II",
    "Firdhan Alfian": "Seksi Pengawasan III",
    "Freddy Irsyam Siregar": "Seksi Pengawasan IV",
    "Gede Kharisma Irawan": "Seksi Pengawasan IV",
    "Hadad Syahiddin": "Seksi Pengawasan V",
    "Harina": "Seksi Pengawasan V",
    "Irfa`I Hasan": "Seksi Pengawasan VI",
    "Jacsen Mariano Sumakul": "Seksi Pengawasan IV",
    "Made Andre Arya Prabawa": "Seksi Pengawasan V",
    "Marissa Kartika Taruly": "Seksi Pengawasan II",
    "Metta Yudhia Harini": "Seksi Pengawasan VI",
    "Mhd Irsyad": "Seksi Pengawasan I",
    "Mohammad Rasyidi": "Seksi Pengawasan III",
    "Muhammad Irfan Yasir": "Seksi Pengawasan V",
    "Nur Hidayat": "Seksi Pengawasan I",
    "Raden Panji Hendi Ardiadi": "Seksi Pengawasan VI",
    "Regy Anggraeni": "Seksi Pengawasan IV",
    "Satria Pradana Gofar": "Seksi Pengawasan III",
    "Siti Khaerunnisa": "Seksi Pengawasan VI",
    "Sokheh Wisnu Wikantoro": "Seksi Pengawasan II",
    "Sri Wahyuni": "Seksi Pengawasan III",
    "Syauqi Ramadhan Putra Utama": "Seksi Pengawasan II",
    "Wida Satria Utama": "Seksi Pengawasan III",
}

# Pemetaan Bulan Teks ke Angka Format 2 Digit
MONTH_MAP = {
    "januari": "01",
    "jan": "01",
    "februari": "02",
    "feb": "02",
    "maret": "03",
    "mar": "03",
    "april": "04",
    "apr": "04",
    "mei": "05",
    "juni": "06",
    "jun": "06",
    "juli": "07",
    "jul": "07",
    "agustus": "08",
    "agu": "08",
    "ags": "08",
    "september": "09",
    "sep": "09",
    "oktober": "10",
    "okt": "10",
    "november": "11",
    "nov": "11",
    "desember": "12",
    "des": "12",
}


def convert_to_yymmdd(raw_date_str):
    """Mengubah format tanggal (e.g. '26 September 2026' atau '26/09/2026') ke format YYMMDD (e.g. '260926')."""
    if not raw_date_str:
        return ""

    match_digits = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", raw_date_str)
    if match_digits:
        day, month, year = match_digits.groups()
        day = f"{int(day):02d}"
        month = f"{int(month):02d}"
        year = year[-2:]
        return f"{year}{month}{day}"

    match_text = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{2,4})", raw_date_str)
    if match_text:
        day, month_name, year = match_text.groups()
        day = f"{int(day):02d}"
        month = MONTH_MAP.get(month_name.lower(), "01")
        year = year[-2:]
        return f"{year}{month}{day}"

    return ""


def extract_data_from_pdf(pdf_file):
    data = {
        "Nama File": pdf_file.name,
        "No / Nomor Surat": "",
        "No Surat (Angka)": "",
        "Nama Pengampu": "",
        "Seksi Pengawasan": "",
        "Unit Organisasi": "",
        "Waktu": "",
        "Nama Wajib Pajak": "",
        "Tanggal Pertemuan": "",
        "Tanggal Short Format": "",
    }

    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    # 1. Ekstrak Nomor Surat & Angka Nomor Surat
    match_no = re.search(r"Nomor\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if match_no:
        full_no = match_no.group(1).strip()
        data["No / Nomor Surat"] = full_no

        # Ambil angka setelah prefiks (misal UND-429 -> 429, S-876 -> 876)
        match_angka = re.search(r"(?:UND|S|ND|ST)[-/\s]*(\d+)", full_no, re.IGNORECASE)
        if match_angka:
            data["No Surat (Angka)"] = match_angka.group(1)
        else:
            # Fallback jika tidak ada awalan teks khusus, ambil sekumpulan angka pertama
            first_num = re.search(r"\d+", full_no)
            data["No Surat (Angka)"] = first_num.group(0) if first_num else ""

    # 2. Ekstrak Nama Wajib Pajak
    match_wp = re.search(
        r"Yth\.\s*(?:Bapak/Ibu\s*|Direktur\s*|Pimpinan\s*)?([^\n]+)",
        text,
        re.IGNORECASE,
    )
    if match_wp:
        data["Nama Wajib Pajak"] = match_wp.group(1).strip()

    # 3. Ekstrak Waktu / Jam
    match_waktu = re.search(
        r"(?:pukul|Waktu)\s*:\s*([^\n]+)", text, re.IGNORECASE
    )
    if match_waktu:
        raw_waktu = match_waktu.group(1).strip()
        jam_match = re.search(r"(\d{2}[\.:]\d{2})", raw_waktu)
        data["Waktu"] = jam_match.group(1) if jam_match else raw_waktu

    # 4. Ekstrak Tanggal Pertemuan & Short Format YYMMDD
    match_tgl = re.search(
        r"Hari\s*[,/]\s*Tanggal\s*:\s*([^\n]+)", text, re.IGNORECASE
    )
    if match_tgl:
        raw_tgl = match_tgl.group(1).strip()

        clean_tgl = re.search(
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            raw_tgl,
        )
        if clean_tgl:
            tgl_str = clean_tgl.group(1).strip()
            data["Tanggal Pertemuan"] = tgl_str
            data["Tanggal Short Format"] = convert_to_yymmdd(tgl_str)
        else:
            tgl_str = (
                raw_tgl.split("/")[-1]
                .split(",")[-1]
                .strip()
            )
            data["Tanggal Pertemuan"] = tgl_str
            data["Tanggal Short Format"] = convert_to_yymmdd(tgl_str)

    # 5. Ekstrak Unit Organisasi / Seksi
    match_seksi = re.search(r"Seksi\s+([^\)\n]+)", text, re.IGNORECASE)
    if match_seksi:
        data["Unit Organisasi"] = f"Pengawasan {match_seksi.group(1).strip()}"

    # 6. Ekstrak Nama Pengampu / AR & Matching Seksi Pengawasan
    nama_ar = ""
    match_ar_f2 = re.search(
        r"Nama\s*:\s*([^\n]+)\s*\n\s*Jabatan\s*:\s*Account Representative",
        text,
        re.IGNORECASE,
    )
    if match_ar_f2:
        nama_ar = match_ar_f2.group(1).strip()
    else:
        match_ar_f1 = re.search(
            r"\d\.\s+([^\(]+)\s*\(\s*Account\s+Representative",
            text,
            re.IGNORECASE,
        )
        if match_ar_f1:
            nama_ar = match_ar_f1.group(1).strip()
        else:
            match_pengampu = re.search(
                r"bertemu dengan\s*:\s*(?:\d\.\s+)?([^\n\()]+)",
                text,
                re.IGNORECASE,
            )
            if match_pengampu:
                nama_ar = match_pengampu.group(1).strip()

    data["Nama Pengampu"] = nama_ar

    if nama_ar in MAPPING_AR_SEKSI:
        data["Seksi Pengawasan"] = MAPPING_AR_SEKSI[nama_ar]
    else:
        found_seksi = ""
        for key_ar, val_seksi in MAPPING_AR_SEKSI.items():
            if key_ar.lower() in nama_ar.lower():
                found_seksi = val_seksi
                break
        data["Seksi Pengawasan"] = found_seksi

    return data


# Form Upload File
uploaded_files = st.file_uploader(
    "Pilih file PDF Surat Undangan", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Berhasil mengunggah {len(uploaded_files)} file PDF.")

    rows = []
    for uploaded_file in uploaded_files:
        parsed_data = extract_data_from_pdf(uploaded_file)
        rows.append(parsed_data)

    df = pd.DataFrame(rows)

    # Reorder kolom sesuai kebutuhan
    cols = [
        "Nama File",
        "No / Nomor Surat",
        "No Surat (Angka)",
        "Nama Pengampu",
        "Seksi Pengawasan",
        "Unit Organisasi",
        "Waktu",
        "Tanggal Pertemuan",
        "Tanggal Short Format",
        "Nama Wajib Pajak",
    ]
    df = df[[c for c in cols if c in df.columns]]

    st.subheader("📊 Hasil Ekstraksi Data")
    st.dataframe(df, use_container_width=True)

    # Export ke format Excel (.xlsx)
    output_excel = "Hasil_Ekstraksi_Surat.xlsx"
    df.to_excel(output_excel, index=False, engine="openpyxl")

    with open(output_excel, "rb") as f:
        st.download_button(
            label="📥 Download File Excel",
            data=f,
            file_name="Data_Undangan_Pembahasan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

def extract_surat_tugas_data(pdf_file):
    text_full = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_full += extracted + "\n"
    except Exception as e:
        st.error(f"Gagal membaca file {pdf_file.name}: {e}")
        return None

    # Clean up double spaces or irregular line breaks
    clean_text = re.sub(r'[ \t]+', ' ', text_full)

    # -------------------------------------------------------------
    # 1. NOMOR SURAT TUGAS (DIPERBAIKI)
    # -------------------------------------------------------------
    nomor_st = "-"
    
    # Pola 1: Mencari frasa yang diawali NOMOR / ST- lalu mengambil seluruh string hingga akhir baris
    # Contoh target: "NOMOR ST-331/KPP.2009/2026" atau "NOMOR : ST-331/KPP.2009/2026"
    st_match = re.search(
        r'(?:NOMOR|ST)\s*[:\.-]?\s*((?:ST\s*[\/:-]?)?\s*[A-Z0-9]+(?:\s*[\/\.-]\s*[A-Z0-9]+)+)', 
        clean_text, 
        re.IGNORECASE
    )

    if st_match:
        # Bersihkan spasi berlebih di dalam nomor ST (misal: "ST - 331" menjadi "ST-331")
        nomor_raw = st_match.group(1).strip()
        nomor_st = re.sub(r'\s*([\/:-])\s*', r'\1', nomor_raw)
    else:
        # Pola Cadangan (Fallback): Cari pola umum format nomor surat kantor dinas/pajak/Kemenkeu
        fallback_match = re.search(r'\b(ST[-/][A-Z0-9\.\/-]+)\b', clean_text, re.IGNORECASE)
        if fallback_match:
            nomor_st = re.sub(r'\s+', '', fallback_match.group(1))

    # -------------------------------------------------------------
    # 2. HARI & TANGGAL PELAKSANAAN
    # -------------------------------------------------------------
    hari_tgl_match = re.search(r'hari\s*[/:\s]*tanggal\s*:\s*([^\n\r]+)', clean_text, re.IGNORECASE)
    
    hari = "-"
    tanggal = "-"
    
    if hari_tgl_match:
        full_hari_tgl = hari_tgl_match.group(1).strip()
        parts = re.split(r'[,/]', full_hari_tgl, maxsplit=1)
        
        if len(parts) == 2:
            hari = parts[0].strip()
            tanggal = parts[1].strip()
        else:
            tanggal = full_hari_tgl

    # 3. WAKTU
    waktu_match = re.search(r'waktu\s*:\s*([^\n\r]+)', clean_text, re.IGNORECASE)
    waktu = waktu_match.group(1).strip() if waktu_match else "-"

    # 4. TEMPAT
    tempat_match = re.search(r'tempat\s*:\s*(.*?)(?=\s*agenda\s*:|\n\s*[a-z]+\s*:|$)', clean_text, re.IGNORECASE | re.DOTALL)
    if tempat_match:
        tempat = " ".join(tempat_match.group(1).split())
    else:
        tempat = "-"

    # 5. AGENDA
    agenda_match = re.search(r'agenda\s*:\s*(.*?)(?=\s*Surat Tugas ini|\s*untuk melaksanakan|\n\n|$)', clean_text, re.IGNORECASE | re.DOTALL)
    if agenda_match:
        agenda = " ".join(agenda_match.group(1).split())
    else:
        agenda = "-"

    # 6. TANGGAL PENETAPAN SURAT
    tgl_surat_match = re.search(r'([A-Za-z]+,\s*\d{1,2}\s+[A-Za-z]+\s+\d{4})', clean_text)
    tanggal_surat_list = re.findall(r'([A-Z][a-z]+,\s*\d{1,2}\s+[A-Z][a-z]+\s+\d{4})', text_full)
    tanggal_surat = tanggal_surat_list[-1] if tanggal_surat_list else (tgl_surat_match.group(1) if tgl_surat_match else "-")

    return {
        "Nama File": pdf_file.name,
        "Nomor ST": nomor_st,
        "Hari": hari,
        "Tanggal Pelaksanaan": tanggal,
        "Waktu": waktu,
        "Tempat": tempat,
        "Agenda": agenda,
        "Tanggal Surat": tanggal_surat
    }

# Interface Streamlit
st.set_page_config(page_title="Ekstraktor Data Surat Tugas", layout="wide")

st.title("📄 Ekstraktor Data Surat Tugas (Batch PDF Processing)")
st.write("Unggah beberapa file Surat Tugas (PDF) untuk mengekstrak data utama secara otomatis ke dalam format tabel/Excel.")

uploaded_files = st.file_uploader(
    "Pilih file PDF Surat Tugas (bisa pilih banyak sekaligus):", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    data_list = []
    
    with st.spinner("Sedang memproses file PDF..."):
        for pdf_file in uploaded_files:
            res = extract_surat_tugas_data(pdf_file)
            if res:
                data_list.append(res)
    
    if data_list:
        df = pd.DataFrame(data_list)
        
        st.subheader(f"Hasil Ekstraksi ({len(data_list)} File)")
        st.dataframe(df, use_container_width=True)

        # Export ke Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data Surat Tugas')
        
        st.download_button(
            label="📥 Download Data Excel",
            data=buffer.getvalue(),
            file_name="rekap_surat_tugas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
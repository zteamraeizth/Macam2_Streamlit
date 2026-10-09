import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

# Pemetaan bulan ke bahasa Indonesia
MONTH_MAP = {
    '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
    '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
    '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
}

def format_date_id(date_str):
    """Mengubah format dd/mm/yyyy menjadi 'dd MMMM yyyy' (contoh: 02/07/2026 -> 02 Juli 2026)"""
    if not date_str:
        return ""
    parts = date_str.strip().split('/')
    if len(parts) == 3:
        day, month, year = parts
        month_name = MONTH_MAP.get(month, month)
        return f"{int(day):02d} {month_name} {year}"
    return date_str

def parse_pdf_nominatif(pdf_file):
    rows = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            
            # 1. Ekstrak 'Dalam Rangka' (Uraian Kegiatan) dari Header
            kegiatan_match = re.search(r"DALAM RANGKA\s*\n?\s*(.*?)(?=\nNomor DNP|\nNomor ST|$)", text, re.DOTALL | re.IGNORECASE)
            kegiatan = kegiatan_match.group(1).replace('\n', ' ').strip() if kegiatan_match else ""
            
            # 2. Ekstrak Nomor ST (Mengambil angka setelah ST-, contoh: ST-415/KPP... -> 415)
            st_match = re.search(r"Nomor ST\s*:\s*ST-(\d+)", text, re.IGNORECASE)
            no_st_val = int(st_match.group(1)) if st_match else ""
            
            # 3. Ekstrak Tabel Rincian Pegawai
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 9:
                        continue
                    
                    # Memastikan baris berisi data pegawai (nomor urut berupa angka: 1, 2, dst)
                    first_cell = str(row[0]).strip() if row[0] else ""
                    if not first_cell.isdigit():
                        continue
                    
                    # --- EXTRAKS NAMA ---
                    nama_nip_raw = str(row[1]).strip() if row[1] else ""
                    # Ganti semua baris baru/enter/spasi ganda menjadi 1 spasi
                    nama_nip_clean = re.sub(r"\s+", " ", nama_nip_raw)
                    # Ambil nama utuh sebelum karakter '/'
                    nama = nama_nip_clean.split('/')[0].strip()

                    # Parse Kolom Tujuan & Tanggal Berangkat
                    tujuan = str(row[3]).strip().title() if row[3] else ""
                    tgl_berangkat_raw = str(row[4]).strip() if row[4] else ""
                    
                    # --- PENYESUAIAN: AMBIL BIAYA DARI KOLOM 'SELISIH LEBIH/KURANG' ---
                    # Urutan Kolom Tabel PDF:
                    # 0: No | 1: Nama/NIP | 2: Instansi | 3: Tujuan | 4: Tgl Berangkat
                    # 5: Jml Hari | 6: Est | 7: Uang Muka | 8: Total Biaya Riil | 9: Selisih Lebih/Kurang
                    
                    biaya_raw = ""
                    if len(row) > 9 and row[9]:
                        biaya_raw = str(row[9]).strip()
                    elif len(row) > 8 and row[8]:
                        biaya_raw = str(row[8]).strip()
                    
                    # Bersihkan karakter teks seperti 'Kurang', 'Rp', titik, dan spasi
                    biaya_clean = re.sub(r"[^\d]", "", biaya_raw)
                    try:
                        biaya_riil = int(biaya_clean) if biaya_clean else 0
                    except ValueError:
                        biaya_riil = 0
                        
                    tgl_formatted = format_date_id(tgl_berangkat_raw)

                    # Susun susunan kolom sesuai format Excel
                    rows.append({
                        "No ST": no_st_val,
                        "Jumlah Hari": 1,
                        "Tgl Berangkat": tgl_formatted,
                        "Tgl Kembali": tgl_formatted,
                        "Nama Pegawai": nama,
                        "Uraian / Dalam Rangka": kegiatan,
                        "Tujuan": tujuan,
                        "Total Biaya Riil": biaya_riil
                    })
                    
    return rows

# Tampilan UI Streamlit
st.set_page_config(page_title="PDF Extractor - Nominatif Perjalanan Dinas", layout="wide")

st.title("📄 PDF to Excel Extractor - Perjalanan Dinas")
st.write("Upload berkas PDF (bisa sekaligus 73 file atau lebih). Sistem akan otomatis membaca seluruh baris pegawai.")

uploaded_files = st.file_uploader("Pilih file PDF", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Total file terunggah: {len(uploaded_files)} file")
    
    if st.button("Proses Seluruh PDF"):
        all_data = []
        progress_bar = st.progress(0)
        
        for idx, file in enumerate(uploaded_files):
            extracted = parse_pdf_nominatif(file)
            all_data.extend(extracted)
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"Selesai! Berhasil mengolah total {len(all_data)} baris data pegawai dari {len(uploaded_files)} file PDF.")
            
            st.subheader("Preview Hasil Ekstraksi Data")
            st.dataframe(df, use_container_width=True)
            
            # Export ke format Excel (.xlsx)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Rekap Nominatif')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download File Excel (.xlsx)",
                data=excel_data,
                file_name="Rekap_Nominatif_Perjalanan_Dinas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Tidak ada baris data pegawai yang terdeteksi pada file PDF yang diunggah.")
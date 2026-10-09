import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Arsip Data", page_icon="📂", layout="wide")

st.title("📂 Pengolah Arsip Data Excel")
st.write("Unggah file Excel arsip data untuk diproses, difilter, dan dikelompokkan secara otomatis.")

# 1. Upload File
uploaded_file = st.file_uploader("Pilih file data Excel", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("💡 Silakan unggah file Excel terlebih dahulu untuk memulai pemrosesan.")
    st.stop()

# 2. Proses File
try:
    # Read Excel langsung dari Streamlit Upload Buffer
    df = pd.read_excel(uploaded_file, header=None)

    # Validasi jumlah kolom minimal 10
    if len(df.columns) < 10:
        st.error("Format file kurang dari 10 kolom! Pastikan kolom A-J berisi data yang sesuai.")
        st.stop()

    # Rename 10 kolom pertama berdasarkan posisi (A-J)
    df = df.rename(columns={
        df.columns[0]: 'nama_wp',
        df.columns[1]: 'npwp',
        df.columns[2]: 'seksi',
        df.columns[3]: 'jenis_berkas',
        df.columns[4]: 'status',
        df.columns[5]: 'bulan',
        df.columns[6]: 'tahun',
        df.columns[7]: 'satuan',
        df.columns[8]: 'tingkat',
        df.columns[9]: 'kondisi'
    })

    # Filter baris: hapus baris yang tahunnya bukan angka
    df = df[pd.to_numeric(df['tahun'], errors='coerce').notna()].copy()

    # Hitung TOTAL DATA INPUT
    total_input = len(df)

    # Format Uraian
    df['jenis_clean'] = df['jenis_berkas'].astype(str).str.replace('Berkas ', '', regex=False)
    df['uraian'] = df['jenis_clean'] + ' a.n. ' + df['nama_wp'].astype(str)

    # Agregasi / Grouping
    df_output = df.groupby(['uraian', 'tahun', 'tingkat', 'kondisi']).agg(
        jumlah_berkas=('bulan', 'count')
    ).reset_index()

    # Susun urutan kolom [Uraian, Tahun, Jumlah, Tingkat, Kondisi]
    df_output = df_output[['uraian', 'tahun', 'jumlah_berkas', 'tingkat', 'kondisi']]
    df_output['tahun'] = df_output['tahun'].astype(int)

    # Hitung TOTAL DATA OUTPUT
    total_output = int(df_output['jumlah_berkas'].sum())

    st.subheader("📊 Crosscheck Total Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Input (Baris Valid)", f"{total_input} item")
    col2.metric("Total Output (Hasil Sum)", f"{total_output} item")
    
    if total_input == total_output:
        col3.success("✅ STATUS: MATCH (Sesuai)")
    else:
        selisih = abs(total_input - total_output)
        col3.error(f"⚠️ STATUS: MISMATCH (Selisih {selisih} item!)")

    st.divider()

    # Tampilkan Tabel Hasil
    st.subheader("📋 Hasil Konversi & Pengelompokan Data")
    st.dataframe(df_output, use_container_width=True)

    # Persiapan Export ke Excel di Memory Buffer
    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
        df_output.to_excel(writer, index=False, sheet_name='Hasil_Konversi')
    output_buffer.seek(0)

    # Tombol Download
    st.download_button(
        label="📥 Download Hasil Konversi (Excel)",
        data=output_buffer,
        file_name="Hasil_Konversi_Arsip_Data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

except Exception as e:
    st.error(f"Terjadi kesalahan saat memproses data: {e}")

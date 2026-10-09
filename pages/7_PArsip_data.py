import pandas as pd
import tkinter as tk
from tkinter import filedialog

# 1. Inisialisasi GUI untuk pilih file
root = tk.Tk()
root.withdraw()

# 2. Pilih File Excel Input
file_path = filedialog.askopenfilename(
    title="Pilih File Excel Input",
    filetypes=[("Excel Files", "*.xlsx *.xls")]
)

if not file_path:
    print("Proses dibatalkan, tidak ada file input yang dipilih.")
else:
    # 3. Baca file Excel
    df = pd.read_excel(file_path, header=None)

    # 4. Rename 10 kolom pertama berdasarkan urutan posisi (A-J)
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

    # 5. Filter baris: hapus baris yang tahunnya bukan angka (misal header/baris kosong)
    df = df[pd.to_numeric(df['tahun'], errors='coerce').notna()].copy()

    # Hitung TOTAL DATA INPUT sebelum digrouping
    total_input = len(df)

    # 6. Format Uraian
    df['jenis_clean'] = df['jenis_berkas'].astype(str).str.replace('Berkas ', '', regex=False)
    df['uraian'] = df['jenis_clean'] + ' a.n. ' + df['nama_wp'].astype(str)

    # 7. Agregasi / Grouping
    df_output = df.groupby(['uraian', 'tahun', 'tingkat', 'kondisi']).agg(
        jumlah_berkas=('bulan', 'count')
    ).reset_index()

    # 8. Susun urutan kolom [Uraian, Tahun, Jumlah, Tingkat, Kondisi]
    df_output = df_output[['uraian', 'tahun', 'jumlah_berkas', 'tingkat', 'kondisi']]
    df_output['tahun'] = df_output['tahun'].astype(int)

    # Hitung TOTAL DATA OUTPUT (Penjumlahan dari kolom jumlah_berkas)
    total_output = df_output['jumlah_berkas'].sum()

    # 9. Tampilkan Hasil di Terminal
    print("\n--- HASIL KONVERSI ---")
    print(df_output.to_string(index=False))

    # 10. CROSSCHECK TOTAL DATA
    print("\n" + "="*45)
    print("           CROSSCHECK DATA TOTAL          ")
    print("="*45)
    print(f"Total Baris Data Input  : {total_input} item")
    print(f"Total Hasil Perhitungan : {total_output} item")
    
    if total_input == total_output:
        print("STATUS                  : MATCH (Sama / Sesuai)")
    else:
        selisih = abs(total_input - total_output)
        print(f"STATUS                  : MISMATCH (Ada selisih {selisih} item!)")
    print("="*45 + "\n")

    # 11. Simpan File Output Secara Manual
    save_path = filedialog.asksaveasfilename(
        title="Simpan File Output Excel",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if save_path:
        df_output.to_excel(save_path, index=False)
        print(f"[OK] File berhasil disimpan di: {save_path}")
    else:
        print("Penyimpanan file dibatalkan oleh pengguna.")
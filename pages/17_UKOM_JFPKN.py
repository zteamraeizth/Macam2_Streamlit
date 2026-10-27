import streamlit as st

# Setup Halaman Streamlit
st.set_page_config(
    page_title="Tryout Interaktif UKOM JF PKN 2026",
    page_icon="📑",
    layout="wide"
)

# -----------------------------------------------------------------------------
# BANK DATA SOAL (Contoh Struktur 300 Soal)
# -----------------------------------------------------------------------------
# Kamu bisa menambahkan daftar soal hingga 300 soal pada list 'bank_soal' di bawah
bank_soal = [
    # MODUL 1: PENGUMUMAN UKOM
    {
        "id": 1,
        "modul": "Pokok Pengumuman Ukom JF PKN 2026",
        "soal": "Bambang adalah seorang pelaksana di KPP Pratama Jakarta Duren Sawit berpendidikan S1 Sistem Informasi. Ia telah menjadi PNS selama 3 tahun, nilai kinerja 'Sangat Baik' 2 tahun terakhir, dan tidak sedang dijatuhi sanksi disiplin. Per 1 Januari 2027 usianya 52 tahun. Pangkat Bambang adalah III/a dengan Grade 10. Apakah Bambang memenuhi syarat mengikuti Ukom JF PKN jenjang Ahli Pertama?",
        "opsi": [
            "A. Tidak memenuhi syarat, karena usia melebihi batas maksimal 50 tahun.",
            "B. Memenuhi syarat, karena jenjang Ahli Pertama mensyaratkan Pangkat III/a s.d. IV/a, S1/D-IV, Grade min 10, dan usia di bawah 54 tahun per 1 Januari 2027.",
            "C. Tidak memenuhi syarat, karena masa kerja minimal PNS adalah 5 tahun.",
            "D. Memenuhi syarat, namun wajib menduduki jabatan AR terlebih dahulu."
        ],
        "kunci": "B",
        "pembahasan": "Berdasarkan Pengumuman PENG-653/P3/PJ.01/2026, syarat jenjang Ahli Pertama yaitu: Pangkat III/a s.d. IV/a, Pendidikan S1/D-IV, Grade minimal 10, masa kerja PNS min 2 tahun, kinerja min baik 2 tahun terakhir, dan usia < 54 tahun per 1 Januari 2027.",
        "halaman": "Halaman 1 (PENG-653/P3/PJ.01/2026)"
    },
    {
        "id": 2,
        "modul": "Pokok Pengumuman Ukom JF PKN 2026",
        "soal": "Siti pernah mengikuti dan lulus UKOM Manajerial & Sosial Kultural (Mansoskul) pada Gelombang II. Pada Gelombang IV 2026 ini Siti mendaftar kembali untuk meningkatkan nilai UKOM Teknis. Bagaimana skema ujian bagi Siti?",
        "opsi": [
            "A. Wajib mengulangi seluruh rangkaian UKOM (Teknis dan Mansoskul).",
            "B. Dikecualikan dari UKOM Mansoskul dan hanya mengikuti UKOM Teknis metode Pilihan Ganda pada 3 s.d. 5 November 2026.",
            "C. Hanya wajib mengikuti UKOM Mansoskul metode Situational Judgement Test (SJT).",
            "D. Tidak diperbolehkan mendaftar lagi."
        ],
        "kunci": "B",
        "pembahasan": "Peserta yang sudah memiliki nilai UKOM Mansoskul dikecualikan dari pelaksanaan UKOM Mansoskul. UKOM Teknis dilaksanakan 3 s.d. 5 Nov 2026 metode Pilihan Ganda.",
        "halaman": "Halaman 1 (PENG-653/P3/PJ.01/2026)"
    },

    # MODUL 2: PMK 15/2025 PEMERIKSAAN PAJAK
    {
        "id": 3,
        "modul": "PMK 15/2025 tentang Pemeriksaan Pajak",
        "soal": "Tim Pemeriksa Pajak melakukan Pemeriksaan Uji Kepatuhan Tipe Terfokus atas SPT Tahunan PPh Badan PT ABC. SPemb disampaikan pada 10 Februari 2026. Berdasarkan PMK 15/2025, berapa jangka waktu pengujian (batas penyampaian SPHP) paling lama?",
        "opsi": [
            "A. 1 Bulan",
            "B. 3 Bulan",
            "C. 5 Bulan",
            "D. 10 Hari Kerja"
        ],
        "kunci": "B",
        "pembahasan": "Sesuai PMK 15/2025 Pasal 6, Jangka Waktu Pengujian untuk Pemeriksaan Uji Kepatuhan Tipe Terfokus adalah paling lama 3 Bulan sejak SPemb disampaikan.",
        "halaman": "Halaman 5 & Halaman 67 (PMK 15/2025)"
    },
    {
        "id": 4,
        "modul": "PMK 15/2025 tentang Pemeriksaan Pajak",
        "soal": "Pemeriksa Pajak melakukan Pemeriksaan Uji Kepatuhan Tipe Lengkap. Jangka Waktu Pengujian akan berakhir pada 30 September 2026. Kapan batas waktu paling lambat Pemeriksa Wajib mulai melakukan Pembahasan Temuan Sementara dengan WP?",
        "opsi": [
            "A. Paling lambat 14 hari sebelum SPHP diterbitkan.",
            "B. Paling lambat 1 bulan sebelum berakhirnya jangka waktu pengujian (30 Agustus 2026).",
            "C. Bersamaan dengan penyampaian SPemb.",
            "D. Pembahasan Temuan Sementara bersifat opsional."
        ],
        "kunci": "B",
        "pembahasan": "PMK 15/2025 mewajibkan Pemeriksa Pajak mulai melakukan Pembahasan Temuan Sementara dengan WP paling lambat 1 bulan sebelum berakhirnya jangka waktu pengujian untuk Tipe Lengkap atau Terfokus.",
        "halaman": "Halaman 69 (Matriks Perubahan PMK 15/2025)"
    },

    # MODUL 3: PBB SEKTOR P5L
    {
        "id": 5,
        "modul": "Pajak Bumi dan Bangunan Sektor P5L",
        "soal": "PT Elang Buana memiliki perkebunan sawit. Rincian bangunan: Kantor 500 m² (Rp700.000/m²), Gudang 1.000 m² (Rp505.000/m²), Pabrik 4.000 m² (Rp365.000/m²). Berapakah total NJOP Bangunan perusahaan tersebut?",
        "opsi": [
            "A. Rp 936.840.000",
            "B. Rp 2.315.000.000",
            "C. Rp 3.251.840.000",
            "D. Rp 3.239.840.000"
        ],
        "kunci": "B",
        "pembahasan": "Perhitungan NJOP Bangunan:\n- Kantor = 500 x 700.000 = Rp 350.000.000\n- Gudang = 1.000 x 505.000 = Rp 505.000.000\n- Pabrik = 4.000 x 365.000 = Rp 1.460.000.000\nTotal NJOP Bangunan = Rp 2.315.000.000.",
        "halaman": "Halaman 58–60 (Contoh Soal PBB Perkebunan)"
    },

    # MODUL 4: SE-9/PJ/2026 (IBK)
    {
        "id": 6,
        "modul": "SE-9/PJ/2026 tentang Akses Informasi Keuangan (IBK)",
        "soal": "KPP Pratama menerbitkan Surat Permintaan IBK kepada Bank X. Berdasarkan SE-9/PJ/2026, berapa lama batas waktu maksimal bagi Lembaga Keuangan untuk memberikan IBK yang diminta?",
        "opsi": [
            "A. 14 Hari Kalender",
            "B. 1 (satu) Bulan",
            "C. 30 Hari Kerja",
            "D. 10 Hari Kerja"
        ],
        "kunci": "B",
        "pembahasan": "Sesuai SE-9/PJ/2026 angka 9 huruf b, Lembaga Keuangan wajib memberikan Informasi dan/atau Bukti Keterangan (IBK) paling lama 1 (satu) bulan terhitung sejak permintaan IBK diterima.",
        "halaman": "Halaman 101 (SE-9/PJ/2026 Angka 9b)"
    },

    # MODUL 5: PMK 111/2025 (PENGAWASAN WP)
    {
        "id": 7,
        "modul": "PMK 111/2025 tentang Pengawasan Kepatuhan WP",
        "soal": "Account Representative mengirimkan SP2DK kepada WP Terdaftar via Akun WP pada tanggal 5 Oktober 2026. Berapa hari jangka waktu standar WP untuk memberikan tanggapan tertulis?",
        "opsi": [
            "A. 7 Hari sejak SP2DK dikirim.",
            "B. 14 Hari terhitung sejak peristiwa diterbitkannya SP2DK via Akun WP.",
            "C. 30 Hari sejak SP2DK diterima.",
            "D. 10 Hari Kerja sejak SP2DK diunggah."
        ],
        "kunci": "B",
        "pembahasan": "Sesuai PMK 111/2025 Pasal 6 ayat (2), tanggapan SP2DK disampaikan WP dalam jangka waktu paling lama 14 hari terhitung sejak peristiwa yang lebih dahulu (dalam hal ini tanggal penerbitan via Akun WP).",
        "halaman": "Halaman 161 & Halaman 209 (PMK 111/2025 Pasal 6)"
    }
]

# -----------------------------------------------------------------------------
# LOGIKA APLIKASI STREAMLIT
# -----------------------------------------------------------------------------
st.title("📑 Tryout Interaktif UKOM JF PKN 2026")
st.subheader("Simulasi Bank Soal Studi Kasus Perpajakan")

# Sidebar Filter & Informasi
st.sidebar.header("Navigation & Filter")
modul_list = ["Semua Modul"] + list(set([s["modul"] for s in bank_soal]))
selected_modul = st.sidebar.selectbox("Pilih Modul Materi:", modul_list)

# Filter Soal berdasarkan Modul
if selected_modul == "Semua Modul":
    filtered_soal = bank_soal
else:
    filtered_soal = [s for s in bank_soal if s["modul"] == selected_modul]

st.sidebar.markdown("---")
st.sidebar.write(f"**Total Soal Tersedia:** {len(filtered_soal)}")

# State Management Jawaban
if "jawaban_user" not in st.session_state:
    st.session_state["jawaban_user"] = {}

# Layout Soal
skor_benar = 0
for idx, item in enumerate(filtered_soal):
    st.markdown(f"### Soal No. {idx+1}")
    st.caption(f"📌 **Modul:** {item['modul']}")
    st.write(item["soal"])

    # Radio Button Pilihan
    pilihan_key = f"soal_{item['id']}"
    pilihan = st.radio(
        "Pilih Jawaban Anda:",
        item["opsi"],
        key=pilihan_key,
        index=None
    )

    # Simpan Jawaban
    if pilihan:
        jawaban_huruf = pilihan.split(".")[0]
        st.session_state["jawaban_user"][item["id"]] = jawaban_huruf

        # Evaluasi Jawaban Langsung
        if jawaban_huruf == item["kunci"]:
            st.success("✅ **Jawaban Anda Benar!**")
            skor_benar += 1
        else:
            st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item['kunci']}**)")

        # Tampilkan Pembahasan & Redaksi PDF
        with st.expander("📖 Lihat Pembahasan & Referensi PDF"):
            st.write(f"**Pembahasan:**\n{item['pembahasan']}")
            st.info(f"📚 **Redaksi PDF:** {item['halaman']}")

    st.markdown("---")

# Rekap Nilai Akhir
if len(st.session_state["jawaban_user"]) > 0:
    st.sidebar.markdown("### 📊 Rekap Nilai Anda")
    total_dijawab = len(st.session_state["jawaban_user"])
    st.sidebar.metric("Soal Dijawab", f"{total_dijawab} / {len(filtered_soal)}")
    st.sidebar.metric("Jawaban Benar", f"{skor_benar}")
    
    nilai_akhir = (skor_benar / len(filtered_soal)) * 100
    st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

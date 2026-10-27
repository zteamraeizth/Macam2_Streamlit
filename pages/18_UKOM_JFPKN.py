import streamlit as st
import json
import os
import random

# Setup Halaman Streamlit
st.set_page_config(
    page_title="Bank Soal UKOM JF PKN 2026",
    page_icon="📚",
    layout="wide"
)

# -----------------------------------------------------------------------------
# MEMBACA FILE SOAL JSON LOKAL (DENGAN MULTI-PATH FALLBACK)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=2)
def load_bank_soal():
    # Jalur 1: Same directory / script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_script = os.path.join(base_dir, "soal_500.json")

    # Jalur 2: Root directory (jika script ini ada di folder /pages)
    path_parent = os.path.join(base_dir, "..", "soal_500.json")

    # Jalur 3: Current working directory
    path_cwd = os.path.join(os.getcwd(), "soal_500.json")

    json_path = None
    if os.path.exists(path_script):
        json_path = path_script
    elif os.path.exists(path_parent):
        json_path = path_parent
    elif os.path.exists(path_cwd):
        json_path = path_cwd

    if json_path:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            st.error(f"Gagal membaca file JSON: {e}")
            return []
    return []

BANK_SOAL = load_bank_soal()

# -----------------------------------------------------------------------------
# APLIKASI UTAMA STREAMLIT
# -----------------------------------------------------------------------------
st.title("📚 Simulasi Bank Soal UKOM JF PKN 2026")
st.subheader("Modul Latihan 500 Soal — 100% Offline & Auto-Update Tampilan")

if not BANK_SOAL:
    st.warning("⚠️ File `soal_500.json` tidak ditemukan atau masih kosong! Pastikan file JSON berada di folder aplikasi.")
else:
    # Sidebar Filters & Control
    st.sidebar.header("🎯 Filter & Navigasi Soal")

    # Filter Modul Materi
    modul_options = ["Semua Modul"] + sorted(list(set(s.get("modul", "Lainnya") for s in BANK_SOAL)))
    selected_modul = st.sidebar.selectbox("Pilih Modul Materi:", modul_options)

    # Filter Tipe Soal (Hafalan / Studi Kasus)
    tipe_options = ["Semua Tipe", "Hafalan", "Studi Kasus"]
    selected_tipe = st.sidebar.selectbox("Pilih Tipe Soal:", tipe_options)

    # Filtering Logic
    filtered_soal = BANK_SOAL
    if selected_modul != "Semua Modul":
        filtered_soal = [s for s in filtered_soal if s.get("modul") == selected_modul]
    if selected_tipe != "Semua Tipe":
        filtered_soal = [s for s in filtered_soal if s.get("tipe") == selected_tipe]

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Pengaturan Tampilan & Acak")

    # Acak Soal Option
    is_random = st.sidebar.checkbox("🔀 Acak Urutan Soal", value=False)
    
    # Simpan/Reset State Pengacakan agar tidak selalu teracak tiap refresh radio button
    filter_key = f"{selected_modul}_{selected_tipe}_{is_random}"
    if "last_filter" not in st.session_state or st.session_state["last_filter"] != filter_key:
        st.session_state["last_filter"] = filter_key
        if is_random:
            random.shuffle(filtered_soal)
    
    # Pilihan Jumlah Soal yang Ingin Ditampilkan
    total_tersedia = len(filtered_soal)
    max_soal_tampil = st.sidebar.slider(
        "Pilih Jumlah Soal Ditampilkan:",
        min_value=1 if total_tersedia > 0 else 0,
        max_value=total_tersedia if total_tersedia > 0 else 1,
        value=min(20, total_tersedia) if total_tersedia > 0 else 0,
        step=1
    )

    # Potong daftar soal sesuai batas jumlah yang dipilih
    soal_ditampilkan = filtered_soal[:max_soal_tampil]

    st.sidebar.markdown("---")
    st.sidebar.write(f"📊 **Total Soal Tampil:** {len(soal_ditampilkan)} dari {len(BANK_SOAL)} Soal")

    # Tombol Reset Jawaban
    if st.sidebar.button("🔄 Reset Jawaban"):
        for key in list(st.session_state.keys()):
            if key.startswith("local_json_"):
                del st.session_state[key]
        st.session_state["user_answers"] = {}
        st.rerun()

    # Session State Jawaban
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {}

    skor_benar = 0

    # Render Soal
    for idx, item in enumerate(soal_ditampilkan):
        soal_id = item.get("id", idx)
        st.markdown(f"### Soal No. {idx + 1}")
        st.caption(f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')}")
        st.write(item.get("soal", ""))

        pilihan_key = f"local_json_{soal_id}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item.get("opsi", []),
            key=pilihan_key,
            index=None
        )

        if pilihan:
            jawaban_huruf = pilihan.split(".")[0].strip()
            st.session_state["user_answers"][soal_id] = jawaban_huruf

            if jawaban_huruf == item.get("kunci"):
                st.success("✅ **Jawaban Anda Benar!**")
                skor_benar += 1
            else:
                st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item.get('kunci')}**)")

            # Redaksi & Penjelasan Halaman PDF
            with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                st.write(f"**Pembahasan:**\n{item.get('pembahasan', '-')}")
                st.info(f"📚 **Rujukan PDF:** {item.get('halaman_ref', '-')}")

        st.markdown("---")

    # Rekap Perolehan Nilai
    if len(st.session_state["user_answers"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Rekap Perolehan Nilai")
        
        # Hitung skor khusus untuk soal yang sedang ditampilkan
        skor_benar_tampil = 0
        dijawab_tampil = 0
        for s in soal_ditampilkan:
            sid = s.get("id", None)
            if sid in st.session_state["user_answers"]:
                dijawab_tampil += 1
                if st.session_state["user_answers"][sid] == s.get("kunci"):
                    skor_benar_tampil += 1

        st.sidebar.metric("Soal Dijawab", f"{dijawab_tampil} / {len(soal_ditampilkan)}")
        st.sidebar.metric("Jawaban Benar", f"{skor_benar_tampil}")
        
        if len(soal_ditampilkan) > 0:
            nilai_akhir = (skor_benar_tampil / len(soal_ditampilkan)) * 100
            st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

import streamlit as st
import json
import os

# Setup Halaman Streamlit
st.set_page_config(
    page_title="Bank Soal UKOM JF PKN 2026",
    page_icon="📚",
    layout="wide"
)

# -----------------------------------------------------------------------------
# MEMBACA FILE SOAL JSON LOKAL (AUTO-REFRESH SENSITIF)
# -----------------------------------------------------------------------------
# Menggunakan ttl=2 agar Streamlit me-refresh data JSON setiap ada perubahan file
@st.cache_data(ttl=2)
def load_bank_soal():
    json_path = os.path.join(os.path.dirname(__file__), "soal_500.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
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
    st.warning("⚠️ File `soal_500.json` tidak ditemukan atau masih kosong! Pastikan file JSON ditaruh di folder yang sama dengan script ini.")
else:
    # Sidebar Filters
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
    st.sidebar.write(f"📊 **Total Soal Tampil:** {len(filtered_soal)} dari {len(BANK_SOAL)} Soal")

    # Session State Jawaban
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {}

    skor_benar = 0

    # Render Soal
    for idx, item in enumerate(filtered_soal):
        st.markdown(f"### Soal No. {idx + 1}")
        st.caption(f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')}")
        st.write(item.get("soal", ""))

        pilihan_key = f"local_json_{item.get('id', idx)}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item.get("opsi", []),
            key=pilihan_key,
            index=None
        )

        if pilihan:
            jawaban_huruf = pilihan.split(".")[0].strip()
            st.session_state["user_answers"][item.get("id", idx)] = jawaban_huruf

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
        total_dijawab = len(st.session_state["user_answers"])
        st.sidebar.metric("Soal Dijawab", f"{total_dijawab} / {len(filtered_soal)}")
        st.sidebar.metric("Jawaban Benar", f"{skor_benar}")
        nilai_akhir = (skor_benar / len(filtered_soal)) * 100
        st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

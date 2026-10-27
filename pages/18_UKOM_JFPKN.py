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
# MEMBACA FILE SOAL JSON LOKAL
# -----------------------------------------------------------------------------
@st.cache_data
def load_bank_soal():
    json_path = os.path.join(os.path.dirname(__file__), "soal_500.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Fallback jika file belum ada
        return []

BANK_SOAL = load_bank_soal()

# -----------------------------------------------------------------------------
# APLIKASI STREAMLIT
# -----------------------------------------------------------------------------
st.title("📚 Simulasi Bank Soal UKOM JF PKN 2026")
st.subheader("100% Offline, Tanpa API Key, Dilengkapi Pembahasan & Redaksi PDF")

if not BANK_SOAL:
    st.error("⚠️ File `soal_500.json` tidak ditemukan! Pastikan file JSON ditaruh di folder yang sama.")
else:
    # Sidebar Filters
    st.sidebar.header("🎯 Filter & Navigasi Soal")

    modul_options = ["Semua Modul"] + sorted(list(set(s["modul"] for s in BANK_SOAL)))
    selected_modul = st.sidebar.selectbox("Pilih Modul Materi:", modul_options)

    tipe_options = ["Semua Tipe", "Hafalan", "Studi Kasus"]
    selected_tipe = st.sidebar.selectbox("Pilih Tipe Soal:", tipe_options)

    # Filtering Logic
    filtered_soal = BANK_SOAL
    if selected_modul != "Semua Modul":
        filtered_soal = [s for s in filtered_soal if s["modul"] == selected_modul]
    if selected_tipe != "Semua Tipe":
        filtered_soal = [s for s in filtered_soal if s["tipe"] == selected_tipe]

    st.sidebar.markdown("---")
    st.sidebar.write(f"📊 **Total Soal Tampil:** {len(filtered_soal)} dari {len(BANK_SOAL)} Soal")

    # Session State Jawaban
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {}

    skor_benar = 0

    # Render Soal
    for idx, item in enumerate(filtered_soal):
        st.markdown(f"### Soal No. {idx + 1}")
        st.caption(f"📌 **Modul:** {item['modul']} | 🧩 **Tipe:** {item['tipe']}")
        st.write(item["soal"])

        pilihan_key = f"local_json_{item['id']}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item["opsi"],
            key=pilihan_key,
            index=None
        )

        if pilihan:
            jawaban_huruf = pilihan.split(".")[0].strip()
            st.session_state["user_answers"][item["id"]] = jawaban_huruf

            if jawaban_huruf == item["kunci"]:
                st.success("✅ **Jawaban Anda Benar!**")
                skor_benar += 1
            else:
                st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item['kunci']}**)")

            # Redaksi & Penjelasan Halaman PDF
            with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                st.write(f"**Pembahasan:**\n{item['pembahasan']}")
                st.info(f"📚 **Rujukan PDF:** {item['halaman_ref']}")

        st.markdown("---")

    # Rekap Nilai Akhir
    if len(st.session_state["user_answers"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Rekap Perolehan Nilai")
        total_dijawab = len(st.session_state["user_answers"])
        st.sidebar.metric("Soal Dijawab", f"{total_dijawab} / {len(filtered_soal)}")
        st.sidebar.metric("Jawaban Benar", f"{skor_benar}")
        nilai_akhir = (skor_benar / len(filtered_soal)) * 100
        st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

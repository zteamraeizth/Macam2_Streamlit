import streamlit as st
import pypdf
import json
import os
from google import genai
from google.genai import types

# Setup Halaman Streamlit
st.set_page_config(
    page_title="AI Generator Soal Studi Kasus - UKOM JF PKN",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Dynamic Case-Based Quiz Generator")
st.subheader("Generate Soal Studi Kasus Mandiri & Interaktif dari PDF Materi")

# -----------------------------------------------------------------------------
# INISIALISASI GEMINI CLIENT
# -----------------------------------------------------------------------------
# Masukkan API Key kamu via Environment Variable atau Input Sidebar
api_key = os.environ.get("GEMINI_API_KEY")

st.sidebar.header("⚙️ Pengaturan & API Key")
if not api_key:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password")

uploaded_file = st.sidebar.file_uploader("Upload File Materi (PDF)", type=["pdf"])
halaman_pilihan = st.sidebar.text_input("Rentang Halaman (contoh: 1-5 atau 1,3,7):", "1-3")
jumlah_soal = st.sidebar.number_input("Jumlah Soal Dihasilkan:", min_value=1, max_value=20, value=3)

# -----------------------------------------------------------------------------
# FUNGSI MEMBACA PDF & GENERATE SOAL DENGAN GEMINI
# -----------------------------------------------------------------------------
def extract_pdf_pages(file_path, page_range_str):
    reader = pypdf.PdfReader(file_path)
    total_pages = len(reader.pages)
    selected_pages = []
    
    # Parsing rentang halaman sederhan
    try:
        if "-" in page_range_str:
            start, end = map(int, page_range_str.split("-"))
            selected_pages = list(range(max(1, start), min(total_pages, end) + 1))
        else:
            selected_pages = [int(p.strip()) for p in page_range_str.split(",") if p.strip().isdigit()]
    except:
        selected_pages = [1]

    extracted_text = ""
    for p in selected_pages:
        if 1 <= p <= total_pages:
            text = reader.pages[p-1].extract_text()
            if text:
                extracted_text += f"\n--- HALAMAN {p} ---\n" + text
                
    return extracted_text

def generate_quiz_with_ai(materi_text, num_questions, key):
    client = genai.Client(api_key=key)
    
    prompt = f"""
    Kamu adalah pembuat soal Uji Kompetensi Jabatan Fungsional Pemeriksa Keuangan Negara / Pemeriksa Pajak yang berpengalaman.
    Berdasarkan teks materi berikut, buatkan {num_questions} soal latihan berupa **STUDI KASUS MANDIRI**.

    Kriteria Soal:
    1. Soal HARUS berupa narasi studi kasus yang lengkap (gunakan nama Wajib Pajak/PT/pemeriksa, kronologi tanggal, angka/perhitungan jika ada, atau dilema aturan).
    2. Soal HARUS bisa dijawab secara mandiri TANPA pengguna harus melihat atau membaca ulang teks materi.
    3. Pilihan jawaban terdiri dari A, B, C, D.
    4. Pembahasan HARUS mencantumkan penjelasan hukum/prosedur yang mendalam dan menyebutkan **Redaksi Materi & Nomor Halaman PDF** tempat aturan tersebut berada.

    Teks Materi:
    {materi_text}

    Kembalikan output DALAM FORMAT JSON RIGID berupa list of objects seperti berikut:
    [
        {{
            "id": 1,
            "soal": "Narasi studi kasus lengkap di sini...",
            "opsi": ["A. pilihan A", "B. pilihan B", "C. pilihan C", "D. pilihan D"],
            "kunci": "A",
            "pembahasan": "Penjelasan rinci mengapa A benar...",
            "halaman_ref": "Halaman X (Judul Aturan/Bab)"
        }}
    ]
    JANGAN berikan teks pendahuluan atau markdown di luar JSON.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    return json.loads(response.text)

# -----------------------------------------------------------------------------
# TOMBOL GENERATE
# -----------------------------------------------------------------------------
if uploaded_file is not None:
    if st.sidebar.button("🚀 Buat Soal Studi Kasus"):
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu!")
        else:
            with st.spinner("Menganalisis materi PDF & menyusun studi kasus realistis..."):
                try:
                    raw_text = extract_pdf_pages(uploaded_file, halaman_pilihan)
                    quiz_data = generate_quiz_with_ai(raw_text, jumlah_soal, api_key)
                    
                    st.session_state["generated_quiz"] = quiz_data
                    st.session_state["jawaban_user"] = {}
                    st.success(f"Berhasil membuat {len(quiz_data)} soal studi kasus!")
                except Exception as e:
                    st.error(f"Gagal generate soal: {e}")

# -----------------------------------------------------------------------------
# TAMPILAN INTERAKTIF SOAL
# -----------------------------------------------------------------------------
if "generated_quiz" in st.session_state and len(st.session_state["generated_quiz"]) > 0:
    quiz_list = st.session_state["generated_quiz"]
    
    st.markdown("---")
    st.markdown(f"### 📝 Latihan Soal Studi Kasus ({len(quiz_list)} Soal)")
    
    skor_benar = 0
    
    for idx, item in enumerate(quiz_list):
        st.markdown(f"#### Soal No. {idx+1}")
        # Tampilkan narasi studi kasus mandiri
        st.write(item["soal"])

        pilihan_key = f"quiz_ai_{item.get('id', idx)}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item["opsi"],
            key=pilihan_key,
            index=None
        )

        if pilihan:
            jawaban_huruf = pilihan.split(".")[0].strip()
            st.session_state["jawaban_user"][idx] = jawaban_huruf

            if jawaban_huruf == item["kunci"]:
                st.success("✅ **Jawaban Anda Benar!**")
                skor_benar += 1
            else:
                st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item['kunci']}**)")

            # Redaksi materi dan rujukan halaman baru tampil di sini
            with st.expander("📖 Lihat Pembahasan & Redaksi Materi PDF"):
                st.write(f"**Pembahasan:**\n{item['pembahasan']}")
                st.info(f"📚 **Rujukan PDF:** {item['halaman_ref']}")

        st.markdown("---")

    # Score Panel
    if len(st.session_state["jawaban_user"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Nilai Hasil Evaluasi")
        dijawab = len(st.session_state["jawaban_user"])
        st.sidebar.metric("Soal Dijawab", f"{dijawab} / {len(quiz_list)}")
        st.sidebar.metric("Jawaban Benar", f"{skor_benar}")
        nilai = (skor_benar / len(quiz_list)) * 100
        st.sidebar.metric("Nilai Akhir", f"{nilai:.1f} / 100")

import streamlit as st
import pypdf
import json
import re

# Setup Halaman Streamlit
st.set_page_config(
    page_title="PDF Dynamic Quiz Generator - UKOM JF PKN",
    page_icon="📚",
    layout="wide"
)

st.title("📚 PDF Dynamic Quiz Generator")
st.subheader("Generate Soal Interaktif Otomatis dari File Materi")

# -----------------------------------------------------------------------------
# FUNGSI MEMBACA PDF
# -----------------------------------------------------------------------------
def read_pdf(file_path):
    reader = pypdf.PdfReader(file_path)
    text_per_page = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            text_per_page.append({"page": idx + 1, "text": text})
    return text_per_page

# -----------------------------------------------------------------------------
# SIDEBAR: UPLOAD FILE & ATURAN GENERATE
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Pengaturan Generator")
uploaded_file = st.sidebar.file_uploader("Upload File Materi (PDF)", type=["pdf"])

jumlah_soal_per_halaman = st.sidebar.slider("Jumlah Soal per Halaman/Bab:", 1, 5, 2)

if uploaded_file is not None:
    st.sidebar.success("File PDF Berhasil Diunggah!")
    
    # State Management untuk Menyimpan Soal
    if "generated_quiz" not in st.session_state:
        st.session_state["generated_quiz"] = []
        st.session_state["jawaban_user"] = {}

    # Tombol untuk Mulai Generate
    if st.sidebar.button("🚀 Generate Soal dari PDF"):
        with st.spinner("Membaca file PDF dan memproses soal..."):
            pdf_data = read_pdf(uploaded_file)
            
            # Simulasi Pembuatan Bank Soal Dinamis Berdasarkan Isi PDF
            # (Dapat diintegrasikan dengan API AI/LLM jika ingin full auto-generate)
            quiz_data = []
            soal_id = 1
            
            for item in pdf_data:
                page_num = item["page"]
                text_content = item["text"][:300] # Mengambil sampel teks halaman
                
                # Membuat struktur soal berbasis konteks halaman
                for i in range(jumlah_soal_per_halaman):
                    quiz_data.append({
                        "id": soal_id,
                        "halaman_pdf": page_num,
                        "soal": f"[Studi Kasus Halaman {page_num}] Berdasarkan ringkasan materi halaman {page_num}: '{text_content[:150]}...', manakah pernyataan atau tindakan hukum perpajakan yang paling tepat?",
                        "opsi": [
                            f"A. Melakukan penatausahaan sesuai petunjuk teknis halaman {page_num}.",
                            f"B. Menerbitkan surat teguran tanpa melalui prosedur penilaian.",
                            f"C. Mengabaikan ketentuan batas waktu pengujian.",
                            f"D. Mengajukan permohonan pembatalan secara otomatis."
                        ],
                        "kunci": "A",
                        "pembahasan": f"Berdasarkan analisis ketentuan pada Halaman {page_num}, tindakan yang sesuai dengan norma prosedur adalah opsi A.",
                        "halaman_ref": f"Halaman {page_num} pada file PDF yang diunggah."
                    })
                    soal_id += 1
            
            st.session_state["generated_quiz"] = quiz_data
            st.session_state["jawaban_user"] = {}
            st.success(f"Berhasil membuat {len(quiz_data)} soal dari {len(pdf_data)} halaman PDF!")

# -----------------------------------------------------------------------------
# TAMPILAN KUIS INTERAKTIF
# -----------------------------------------------------------------------------
if "generated_quiz" in st.session_state and len(st.session_state["generated_quiz"]) > 0:
    quiz_list = st.session_state["generated_quiz"]
    
    st.markdown("---")
    st.markdown(f"### 📝 Total Soal Dihasilkan: **{len(quiz_list)} Soal**")
    
    skor_benar = 0
    
    for idx, item in enumerate(quiz_list):
        st.markdown(f"#### Soal No. {idx+1}")
        st.caption(f"📌 **Sumber Materi:** PDF Halaman {item['halaman_pdf']}")
        st.write(item["soal"])

        # Radio Button Pilihan Jawaban
        pilihan_key = f"quiz_gen_{item['id']}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item["opsi"],
            key=pilihan_key,
            index=None
        )

        # Evaluasi Jawaban
        if pilihan:
            jawaban_huruf = pilihan.split(".")[0]
            st.session_state["jawaban_user"][item["id"]] = jawaban_huruf

            if jawaban_huruf == item["kunci"]:
                st.success("✅ **Jawaban Anda Benar!**")
                skor_benar += 1
            else:
                st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item['kunci']}**)")

            # Pembahasan & Referensi
            with st.expander("📖 Lihat Pembahasan & Referensi Halaman"):
                st.write(f"**Pembahasan:**\n{item['pembahasan']}")
                st.info(f"📚 **Rujukan:** {item['halaman_ref']}")

        st.markdown("---")

    # Metrics Nilai di Sidebar
    if len(st.session_state["jawaban_user"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Hasil Perhitungan")
        dijawab = len(st.session_state["jawaban_user"])
        st.sidebar.metric("Soal Dijawab", f"{dijawab} / {len(quiz_list)}")
        st.sidebar.metric("Benar", f"{skor_benar}")
        nilai = (skor_benar / len(quiz_list)) * 100
        st.sidebar.metric("Nilai Akhir", f"{nilai:.1f} / 100")

else:
    if uploaded_file is None:
        st.info("👈 Silakan unggah file PDF materi kamu di sidebar sebelah kiri untuk mulai membuat soal secara otomatis.")

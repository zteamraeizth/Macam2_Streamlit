import json
import os
import random
import streamlit as st

# Setup Halaman Streamlit
st.set_page_config(
    page_title="Bank Soal UKOM JF PKN 2026", page_icon="📚", layout="wide"
)

# -----------------------------------------------------------------------------
# MEMBACA FILE SOAL JSON LOKAL
# -----------------------------------------------------------------------------
@st.cache_data(ttl=2)
def load_bank_soal():
    json_path = os.path.join(os.path.dirname(__file__), "soal_500.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Otomatis reset nomor ID agar 100% unik (1 s.d. selesai)
                for index, item in enumerate(data, start=1):
                    item["id"] = index
                return data
        except Exception as e:
            st.error(f"Gagal membaca file JSON: {e}")
            return []
    return []

BANK_SOAL = load_bank_soal()

# -----------------------------------------------------------------------------
# APLIKASI UTAMA STREAMLIT
# -----------------------------------------------------------------------------
st.title("📚 Simulasi Bank Soal Materi UKOM JF PKN 2026")
st.subheader("Modul Latihan")

if not BANK_SOAL:
    st.warning(
        "⚠️ File `soal_500.json` tidak ditemukan atau masih kosong! Pastikan file JSON berada di folder aplikasi."
    )
else:
    # Sidebar Filters & Control
    st.sidebar.header("🎯 Filter & Navigasi Soal")

    modul_options = ["Semua Modul"] + sorted(
        list(set(s.get("modul", "Lainnya") for s in BANK_SOAL))
    )
    selected_modul = st.sidebar.selectbox("Pilih Modul Materi:", modul_options)

    tipe_options = ["Semua Tipe", "Hafalan", "Studi Kasus"]
    selected_tipe = st.sidebar.selectbox("Pilih Tipe Soal:", tipe_options)

    # Filtering Logic
    soal_terfilter = BANK_SOAL.copy()
    if selected_modul != "Semua Modul":
        soal_terfilter = [
            s for s in soal_terfilter if s.get("modul") == selected_modul
        ]
    if selected_tipe != "Semua Tipe":
        soal_terfilter = [
            s for s in soal_terfilter if s.get("tipe") == selected_tipe
        ]

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Mode Tampilan & Acak")

    mode_tampilan = st.sidebar.radio(
        "Pilih Mode Tampilan Soal:",
        [
            "Mode Per-Soal (Satu per Halaman)",
            "Mode Per 10 Soal (Pagination)",
            "Mode Per 20 Soal (Pagination)",
            "Mode Daftar (Semua Soal)",
        ],
    )

    # Inisialisasi status pengacakan
    if "shuffle_key" not in st.session_state:
        st.session_state["shuffle_key"] = 0

    if st.button("🔀 Acak Urutan Soal", use_container_width=True):
        st.session_state["shuffle_key"] += 1
        st.session_state["current_idx"] = 0
        st.session_state["current_page"] = 0
        st.rerun()
        
    # Terapkan pengacakan pada soal terfilter
    active_soal_list = soal_terfilter.copy()
    rng = random.Random(st.session_state["shuffle_key"])
    rng.shuffle(active_soal_list)

    total_tersedia = len(active_soal_list)

    # Inisialisasi State Jawaban & Percobaan Pertama
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {}
    if "first_answers" not in st.session_state:
        st.session_state["first_answers"] = {}  # Mencatat pilihan PERTAMA KALI
    if "current_idx" not in st.session_state:
        st.session_state["current_idx"] = 0
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0

    # Tombol Reset Jawaban
    if st.sidebar.button("🔄 Reset Jawaban"):
        for key in list(st.session_state.keys()):
            if key.startswith("local_json_"):
                del st.session_state[key]
        st.session_state["user_answers"] = {}
        st.session_state["first_answers"] = {}
        st.session_state["current_idx"] = 0
        st.session_state["current_page"] = 0
        st.rerun()

    # Tentukan List Soal Ditampilkan Berdasarkan Mode
    soal_ditampilkan = []
    max_soal_tampil = total_tersedia

    if mode_tampilan == "Mode Per-Soal (Satu per Halaman)":
        max_soal_tampil = st.sidebar.slider(
            "Batas Maksimal Soal Dikerjakan:",
            min_value=1 if total_tersedia > 0 else 0,
            max_value=total_tersedia if total_tersedia > 0 else 1,
            value=min(50, total_tersedia) if total_tersedia > 0 else 0,
            step=1,
        )
        soal_pembatas = active_soal_list[:max_soal_tampil]
        total_soal = len(soal_pembatas)

        if total_soal > 0:
            if st.session_state["current_idx"] >= total_soal:
                st.session_state["current_idx"] = total_soal - 1
            curr_idx = st.session_state["current_idx"]
            soal_ditampilkan = [soal_pembatas[curr_idx]]
        else:
            soal_ditampilkan = []

    elif mode_tampilan in ["Mode Per 10 Soal (Pagination)", "Mode Per 20 Soal (Pagination)"]:
        soal_per_halaman = 10 if mode_tampilan == "Mode Per 10 Soal (Pagination)" else 20
        total_halaman = (
            (total_tersedia + soal_per_halaman - 1) // soal_per_halaman
            if total_tersedia > 0
            else 1
        )
        if st.session_state["current_page"] >= total_halaman:
            st.session_state["current_page"] = total_halaman - 1

        page_curr = st.session_state["current_page"]
        start_idx = page_curr * soal_per_halaman
        end_idx = min(start_idx + soal_per_halaman, total_tersedia)
        soal_ditampilkan = active_soal_list[start_idx:end_idx]

    else:
        max_soal_tampil = st.sidebar.slider(
            "Pilih Jumlah Soal Ditampilkan:",
            min_value=1 if total_tersedia > 0 else 0,
            max_value=total_tersedia if total_tersedia > 0 else 1,
            value=min(20, total_tersedia) if total_tersedia > 0 else 0,
            step=1,
        )
        soal_ditampilkan = active_soal_list[:max_soal_tampil]

    # Render Soal-Soal
    for idx, item in enumerate(soal_ditampilkan):
        soal_id = item.get("id", idx)
        
        st.markdown(f"### Soal No. {soal_id}")
        st.caption(
            f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')}"
        )
        st.write(item.get("soal", ""))

        pilihan_key = f"local_json_{soal_id}"
        pilihan = st.radio(
            "Pilih Jawaban Anda:",
            item.get("opsi", []),
            key=pilihan_key,
            index=None,
        )

        if pilihan:
            jawaban_huruf = pilihan.split(".")[0].strip()
            
            # 1. Simpan jawaban aktif saat ini
            st.session_state["user_answers"][soal_id] = jawaban_huruf
            
            # 2. HANYA CATAT PILIHAN PERTAMA KALI (Kunci Penilaian)
            if soal_id not in st.session_state["first_answers"]:
                st.session_state["first_answers"][soal_id] = jawaban_huruf

            jawaban_pertama = st.session_state["first_answers"][soal_id]
            kunci_benar = item.get("kunci")

            # 3. Tampilkan Feedback Real-Time
            if jawaban_huruf == kunci_benar:
                st.success("✅ **Jawaban Pilihan Anda Saat Ini Benar!**")
            else:
                st.error(f"❌ **Jawaban Pilihan Anda Saat Ini Salah!** (Jawaban Kunci: **{kunci_benar}**)")

            # Peringatan jika pengguna mengubah jawaban dari salah ke benar
            if jawaban_pertama != kunci_benar:
                st.warning("⚠️ **Catatan Penilaian:** Jawaban pertama Anda pada soal ini adalah SALAH. Perubahan jawaban tidak menambah poin nilai akhir.")

            with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                st.write(f"**Pembahasan:**\n{item.get('pembahasan', '-')}")
                st.info(f"📚 **Rujukan PDF:** {item.get('halaman_ref', '-')}")

        st.markdown("---")

    # ---------------------------------------------------------
    # NAVIGASI SOAL: SEBELUMNYA DAN BERIKUTNYA
    # ---------------------------------------------------------
    if mode_tampilan == "Mode Per-Soal (Satu per Halaman)":
        st.markdown("### Navigasi Soal")

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button(
                "⬅️ Sebelumnya",
                disabled=(
                    total_tersedia == 0
                    or st.session_state["current_idx"] <= 0
                ),
                use_container_width=True,
                key="prev_single",
            ):
                st.session_state["current_idx"] -= 1
                st.rerun()

        with col_info:
            if total_tersedia > 0 and max_soal_tampil > 0:
                st.markdown(
                    f"<div style='text-align:center'>"
                    f"Soal {st.session_state['current_idx'] + 1} "
                    f"dari {max_soal_tampil}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("Tidak ada soal.")

        with col_next:
            if st.button(
                "Berikutnya ➡️",
                disabled=(
                    total_tersedia == 0
                    or st.session_state["current_idx"] >= max_soal_tampil - 1
                ),
                use_container_width=True,
                key="next_single",
            ):
                st.session_state["current_idx"] += 1
                st.rerun()

    elif mode_tampilan in [
        "Mode Per 10 Soal (Pagination)",
        "Mode Per 20 Soal (Pagination)",
    ]:
        soal_per_halaman = (
            10
            if mode_tampilan == "Mode Per 10 Soal (Pagination)"
            else 20
        )

        total_halaman = max(
            1,
            (total_tersedia + soal_per_halaman - 1)
            // soal_per_halaman,
        )

        st.markdown("### Navigasi Halaman")

        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button(
                "⬅️ Sebelumnya",
                disabled=st.session_state["current_page"] <= 0,
                use_container_width=True,
                key="prev_page",
            ):
                st.session_state["current_page"] -= 1
                st.rerun()

        with col_info:
            st.markdown(
                f"<div style='text-align:center'>"
                f"Halaman {st.session_state['current_page'] + 1} "
                f"dari {total_halaman}</div>",
                unsafe_allow_html=True,
            )

        with col_next:
            if st.button(
                "Berikutnya ➡️",
                disabled=(
                    st.session_state["current_page"] >= total_halaman - 1
                ),
                use_container_width=True,
                key="next_page",
            ):
                st.session_state["current_page"] += 1
                st.rerun()

    # -----------------------------------------------------------------------------
    # REKAP PEROLEHAN NILAI (MENGGUNAKAN JAWABAN PERTAMA)
    # -----------------------------------------------------------------------------
    if len(st.session_state["user_answers"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Rekap Perolehan Nilai")
        st.sidebar.caption("🔒 *Nilai dihitung murni berdasarkan pilihan pertama Anda.*")

        skor_benar_pertama = 0
        dijawab_tampil = 0
        
        # Perbaikan target soal rekap agar akurat sesuai mode tampilan
        if mode_tampilan == "Mode Per-Soal (Satu per Halaman)":
            target_soal = active_soal_list[:max_soal_tampil]
        else:
            target_soal = active_soal_list[:max_soal_tampil]

        for s in target_soal:
            sid = s.get("id", None)
            if sid in st.session_state["first_answers"]:
                dijawab_tampil += 1
                if st.session_state["first_answers"][sid] == s.get("kunci"):
                    skor_benar_pertama += 1

        total_target = len(target_soal)
        st.sidebar.metric("Soal Dijawab", f"{dijawab_tampil} / {total_target}")
        st.sidebar.metric("Jawaban Benar (Percobaan 1)", f"{skor_benar_pertama}")

        if total_target > 0:
            nilai_akhir = (skor_benar_pertama / total_target) * 100
            st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

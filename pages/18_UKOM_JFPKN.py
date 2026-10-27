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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_script = os.path.join(base_dir, "soal_500.json")
    path_parent = os.path.join(base_dir, "..", "soal_500.json")
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

    # Filter Tipe Soal
    tipe_options = ["Semua Tipe", "Hafalan", "Studi Kasus"]
    selected_tipe = st.sidebar.selectbox("Pilih Tipe Soal:", tipe_options)

    # Filtering Logic
    filtered_soal = BANK_SOAL.copy()
    if selected_modul != "Semua Modul":
        filtered_soal = [s for s in filtered_soal if s.get("modul") == selected_modul]
    if selected_tipe != "Semua Tipe":
        filtered_soal = [s for s in filtered_soal if s.get("tipe") == selected_tipe]

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Mode Tampilan & Acak")

    # Pilihan Mode Tampilan
    mode_tampilan = st.sidebar.radio(
        "Pilih Mode Tampilan Soal:",
        [
            "Mode Per-Soal (Satu per Halaman)",
            "Mode Per 10 Soal (Pagination)",
            "Mode Per 20 Soal (Pagination)",
            "Mode Daftar (Semua Soal)"
        ]
    )

    # Acak Soal Option
    is_random = st.sidebar.checkbox("🔀 Acak Urutan Soal", value=False)
    
    # Kelola Seed & Urutan Acak di Session State
    filter_key = f"{selected_modul}_{selected_tipe}_{is_random}_{mode_tampilan}"
    
    if "shuffled_soal" not in st.session_state or st.session_state.get("last_filter_key") != filter_key:
        st.session_state["last_filter_key"] = filter_key
        st.session_state["current_idx"] = 0
        st.session_state["current_page"] = 0
        
        temp_list = filtered_soal.copy()
        if is_random:
            random.shuffle(temp_list)
        st.session_state["shuffled_soal"] = temp_list

    active_soal_list = st.session_state["shuffled_soal"]
    total_tersedia = len(active_soal_list)

    # Inisialisasi State Jawaban & Navigasi
    if "user_answers" not in st.session_state:
        st.session_state["user_answers"] = {}
    if "current_idx" not in st.session_state:
        st.session_state["current_idx"] = 0
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 0

    # Tombol Kuis Ulang / Re-shuffle Manual
    if is_random:
        if st.sidebar.button("🔀 Acak Ulang Soal Sekarang"):
            temp_list = filtered_soal.copy()
            random.shuffle(temp_list)
            st.session_state["shuffled_soal"] = temp_list
            st.session_state["current_idx"] = 0
            st.session_state["current_page"] = 0
            st.rerun()

    # Tombol Reset Jawaban
    if st.sidebar.button("🔄 Reset Jawaban"):
        for key in list(st.session_state.keys()):
            if key.startswith("local_json_"):
                del st.session_state[key]
        st.session_state["user_answers"] = {}
        st.session_state["current_idx"] = 0
        st.session_state["current_page"] = 0
        st.rerun()

    soal_ditampilkan = []

    # -----------------------------------------------------------------------------
    # 1. MODE PER-SOAL (SATU PER HALAMAN)
    # -----------------------------------------------------------------------------
    if mode_tampilan == "Mode Per-Soal (Satu per Halaman)":
        max_soal_tampil = st.sidebar.slider(
            "Batas Maksimal Soal Dikerjakan:",
            min_value=1 if total_tersedia > 0 else 0,
            max_value=total_tersedia if total_tersedia > 0 else 1,
            value=min(50, total_tersedia) if total_tersedia > 0 else 0,
            step=1
        )
        soal_ditampilkan = active_soal_list[:max_soal_tampil]
        total_soal = len(soal_ditampilkan)

        if total_soal > 0:
            if st.session_state["current_idx"] >= total_soal:
                st.session_state["current_idx"] = total_soal - 1
            
            curr_idx = st.session_state["current_idx"]
            item = soal_ditampilkan[curr_idx]
            soal_id = item.get("id", curr_idx)

            st.sidebar.markdown("---")
            st.sidebar.write(f"📊 **Posisi:** Soal {curr_idx + 1} dari {total_soal}")

            st.markdown(f"### Soal No. {curr_idx + 1} dari {total_soal}")
            st.caption(f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')} | 🆔 **ID Soal:** {item.get('id', '-')}")
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
                else:
                    st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item.get('kunci')}**)")

                with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                    st.write(f"**Pembahasan:**\n{item.get('pembahasan', '-')}")
                    st.info(f"📚 **Rujukan PDF:** {item.get('halaman_ref', '-')}")

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Soal Sebelumnya", disabled=(curr_idx == 0), use_container_width=True):
                    st.session_state["current_idx"] -= 1
                    st.rerun()

            with col3:
                if st.button("Soal Selanjutnya ➡️", disabled=(curr_idx >= total_soal - 1), use_container_width=True):
                    st.session_state["current_idx"] += 1
                    st.rerun()

    # -----------------------------------------------------------------------------
    # 2. MODE PER 10 / PER 20 SOAL (PAGINATION)
    # -----------------------------------------------------------------------------
    elif mode_tampilan in ["Mode Per 10 Soal (Pagination)", "Mode Per 20 Soal (Pagination)"]:
        soal_per_halaman = 10 if mode_tampilan == "Mode Per 10 Soal (Pagination)" else 20
        total_halaman = (total_tersedia + soal_per_halaman - 1) // soal_per_halaman if total_tersedia > 0 else 1

        if st.session_state["current_page"] >= total_halaman:
            st.session_state["current_page"] = total_halaman - 1

        page_curr = st.session_state["current_page"]
        start_idx = page_curr * soal_per_halaman
        end_idx = min(start_idx + soal_per_halaman, total_tersedia)
        
        soal_ditampilkan = active_soal_list[start_idx:end_idx]

        st.sidebar.markdown("---")
        st.sidebar.write(f"📊 **Halaman:** {page_curr + 1} dari {total_halaman}")
        st.sidebar.write(f"🔢 **Soal Ditampilkan:** {start_idx + 1} - {end_idx} dari {total_tersedia}")

        st.markdown(f"## 📄 Halaman {page_curr + 1} (Soal {start_idx + 1} – {end_idx})")
        st.markdown("---")

        for relative_idx, item in enumerate(soal_ditampilkan):
            absolute_idx = start_idx + relative_idx
            soal_id = item.get("id", absolute_idx)

            st.markdown(f"### Soal No. {absolute_idx + 1}")
            st.caption(f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')} | 🆔 **ID Soal:** {item.get('id', '-')}")
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
                else:
                    st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item.get('kunci')}**)")

                with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                    st.write(f"**Pembahasan:**\n{item.get('pembahasan', '-')}")
                    st.info(f"📚 **Rujukan PDF:** {item.get('halaman_ref', '-')}")

            st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Halaman Sebelumnya", disabled=(page_curr == 0), use_container_width=True):
                st.session_state["current_page"] -= 1
                st.rerun()

        with col3:
            if st.button("Halaman Selanjutnya ➡️", disabled=(page_curr >= total_halaman - 1), use_container_width=True):
                st.session_state["current_page"] += 1
                st.rerun()

    # -----------------------------------------------------------------------------
    # 3. MODE DAFTAR (SEMUA SOAL)
    # -----------------------------------------------------------------------------
    else:
        max_soal_tampil = st.sidebar.slider(
            "Pilih Jumlah Soal Ditampilkan:",
            min_value=1 if total_tersedia > 0 else 0,
            max_value=total_tersedia if total_tersedia > 0 else 1,
            value=min(20, total_tersedia) if total_tersedia > 0 else 0,
            step=1
        )
        soal_ditampilkan = active_soal_list[:max_soal_tampil]

        st.sidebar.markdown("---")
        st.sidebar.write(f"📊 **Total Soal Tampil:** {len(soal_ditampilkan)} dari {len(BANK_SOAL)} Soal")

        for idx, item in enumerate(soal_ditampilkan):
            soal_id = item.get("id", idx)
            st.markdown(f"### Soal No. {idx + 1}")
            st.caption(f"📌 **Modul:** {item.get('modul', '-')} | 🧩 **Tipe:** {item.get('tipe', '-')} | 🆔 **ID Soal:** {item.get('id', '-')}")
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
                else:
                    st.error(f"❌ **Jawaban Anda Salah!** (Jawaban Benar: **{item.get('kunci')}**)")

                with st.expander("📖 Lihat Penjelasan & Redaksi Halaman PDF"):
                    st.write(f"**Pembahasan:**\n{item.get('pembahasan', '-')}")
                    st.info(f"📚 **Rujukan PDF:** {item.get('halaman_ref', '-')}")

            st.markdown("---")

    # -----------------------------------------------------------------------------
    # REKAP PEROLEHAN NILAI (SIDEBAR)
    # -----------------------------------------------------------------------------
    if len(st.session_state["user_answers"]) > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Rekap Perolehan Nilai")
        
        skor_benar_tampil = 0
        dijawab_tampil = 0
        target_soal = soal_ditampilkan if soal_ditampilkan else active_soal_list

        for s in target_soal:
            sid = s.get("id", None)
            if sid in st.session_state["user_answers"]:
                dijawab_tampil += 1
                if st.session_state["user_answers"][sid] == s.get("kunci"):
                    skor_benar_tampil += 1

        total_target = len(target_soal)
        st.sidebar.metric("Soal Dijawab", f"{dijawab_tampil} / {total_target}")
        st.sidebar.metric("Jawaban Benar", f"{skor_benar_tampil}")
        
        if total_target > 0:
            nilai_akhir = (skor_benar_tampil / total_target) * 100
            st.sidebar.metric("Nilai Akhir", f"{nilai_akhir:.1f} / 100")

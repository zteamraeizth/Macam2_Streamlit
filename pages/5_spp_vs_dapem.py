import re
import fitz  # PyMuPDF
import pandas as pd
import streamlit as st


# ================= FUNGSI HELPER & CLEANSING =================
def clean_number(val_str):
    """Mengubah format string angka akuntansi menjadi float."""
    if not val_str:
        return 0.0
    cleaned = re.sub(r"[^\d.,]", "", str(val_str))
    if not cleaned:
        return 0.0

    if "," in cleaned:
        cleaned = cleaned.split(",")[0]

    cleaned = cleaned.replace(".", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_st_number(text):
    """Mengekstrak nomor Surat Tugas (ST) dengan menangani pemotongan baris (line break)."""
    if not text:
        return "-"

    normalized_text = re.sub(r"ST-\s*[\r\n]+\s*", "ST-", text, flags=re.IGNORECASE)
    normalized_text = re.sub(r"/\s*[\r\n]+\s*", "/", normalized_text)

    match = re.search(r"ST-\d+/[A-Z0-9.]+/\d{4}", normalized_text, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return "-"


def normalize_name(name):
    """Normalisasi nama untuk penanganan singkatan/spasi."""
    if not name:
        return ""
    name = name.upper()
    name = re.sub(r"\bM\.\b|\bM\b", "MUHAMMAD", name)
    name = re.sub(r"\bMDR\.\b", "MUHAMMAD", name)
    name = re.sub(r"[^\w\s]", " ", name)
    return " ".join(name.split())


def remove_ppk_signatures(text):
    """Hapus teks area TTD Pejabat/PPK agar Nama Pejabat PPK tidak terdeteksi sebagai penerima."""
    if not text:
        return ""

    cleaned = re.sub(
        r"Pejabat Pembuat Komitmen[\s\S]*?(?:NIP|\n\n|$)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"a\.n\s*Kuasa Pengguna Anggaran[\s\S]*?(?:NIP|\n\n|$)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"DEVRI OSKANDAR\s*\n\s*NIP", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def is_name_matched(name1, name2_text):
    """Mengecek kecocokan nama fleksibel antara DNP dan teks SPP."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2_text)

    if not n1 or not n2:
        return False

    if n1 in n2 or n2 in n1:
        return True

    words1 = [w for w in n1.split() if len(w) > 2]
    words2 = [w for w in n2.split() if len(w) > 2]

    matched = set(words1).intersection(set(words2))
    if len(words1) <= 2 and len(matched) >= 1:
        return True
    if len(words1) > 2 and len(matched) >= 2:
        return True

    return False


# ================= EKSTRAKSI DNP =================
def extract_dnp_data_advanced(dnp_pdf_bytes, filename):
    """Ekstraksi data DNP per individu secara akurat."""
    doc = fitz.open(stream=dnp_pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    st_no = extract_st_number(full_text)
    penerima_list = []

    lines = full_text.split("\n")
    individual_lines = [
        line
        for line in lines
        if "JUMLAH" not in line.upper() and "TOTAL" not in line.upper()
    ]
    text_without_total = "\n".join(individual_lines)

    pola_pegawai = re.findall(
        r"([A-Za-z\s'\.,]+)\s*/\s*(\d{18}|\d{9})", text_without_total
    )
    nominal_matches = re.findall(
        r"(?:Kurang|Lebih)\s*(?:Rp)?\s*([\d\.,]+)",
        text_without_total,
        re.IGNORECASE,
    )
    nominals = [clean_number(amt) for amt in nominal_matches]

    if pola_pegawai:
        for idx, (nama_raw, nip) in enumerate(pola_pegawai):
            nama_clean = nama_raw.strip()
            if "NAMA" in nama_clean.upper() or len(nama_clean) < 3:
                continue

            nominal = nominals[idx] if idx < len(nominals) else 0.0

            penerima_list.append(
                {
                    "dnp_file": filename,
                    "st_no": st_no,
                    "nama": nama_clean.upper(),
                    "nominal": nominal,
                }
            )

    return {"filename": filename, "st_no": st_no, "penerima": penerima_list}


# ================= EKSTRAKSI SPP =================
def extract_spp_data_strict(spp_pdf_bytes, filename):
    """Mengekstrak SPP dengan mengisolasi blok teks per baris."""
    doc = fitz.open(stream=spp_pdf_bytes, filetype="pdf")
    p1_text = doc[0].get_text("text") if len(doc) > 0 else ""
    p2_text = doc[1].get_text("text") if len(doc) > 1 else ""

    st_no = extract_st_number(p1_text)
    if st_no == "-":
        st_no = extract_st_number(p2_text)

    p1_clean = remove_ppk_signatures(p1_text)
    p2_clean = remove_ppk_signatures(p2_text)

    penerima_records = []
    target_text = p2_clean if len(p2_clean.strip()) > 50 else p1_clean
    lines = target_text.split("\n")

    for i, line in enumerate(lines):
        amounts = re.findall(r"\b\d{1,3}(?:\.\d{3})*(?:,\d{2})?\b", line)
        valid_nominals = [
            clean_number(a) for a in amounts if clean_number(a) >= 10000
        ]

        if valid_nominals:
            start_idx = max(0, i - 2)
            end_idx = min(len(lines), i + 3)
            context_block = " ".join(lines[start_idx:end_idx])

            for nom in valid_nominals:
                penerima_records.append(
                    {"context_text": context_block, "nominal": nom}
                )

    return {
        "filename": filename,
        "st_no": st_no,
        "penerima_records": penerima_records,
    }


# ================= CONFIG & SESSION STATE =================
st.set_page_config(
    page_title="Verifikasi Multi-Dokumen DNP & SPP", layout="wide"
)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def clear_all_files():
    st.session_state.uploader_key += 1


# ================= HEADER =================
st.title("📄 Aplikasi Verifikasi & Analisis Multi-Dokumen (DNP vs SPP)")
st.write(
    "Verifikasi presisi Nomor ST, Nama Penerima, dan Kesesuaian Nominal yang Dibayarkan."
)

col_h1, col_h2 = st.columns([8, 2])
with col_h2:
    st.button(
        "🗑️ Clear All Dokumen",
        on_click=clear_all_files,
        type="secondary",
        use_container_width=True,
    )

st.markdown("---")

# ================= UPLOAD FILE =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Dokumen Input (DNP)")
    input_pdfs = st.file_uploader(
        "Upload PDF DNP",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"dnp_{st.session_state.uploader_key}",
    )

with col2:
    st.subheader("2. Upload Dokumen Output (SPP)")
    output_pdfs = st.file_uploader(
        "Upload PDF SPP",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"spp_{st.session_state.uploader_key}",
    )

st.markdown("---")

# ================= PROSES ANALISIS =================
if st.button("🔍 Jalankan Analisis & Pencocokan", type="primary"):
    if not input_pdfs or not output_pdfs:
        st.warning(
            "Harap unggah minimal 1 Dokumen Input (DNP) dan 1 Dokumen Output (SPP)."
        )
    else:
        # 1. Ekstraksi DNP
        all_dnp_targets = []
        dnp_summary = []

        for dnp_file in input_pdfs:
            bytes_data = dnp_file.read()
            dnp_res = extract_dnp_data_advanced(bytes_data, dnp_file.name)
            dnp_summary.append(
                {
                    "Nama File DNP": dnp_res["filename"],
                    "Nomor ST": dnp_res["st_no"],
                    "Penerima Terdeteksi": len(dnp_res["penerima"]),
                }
            )
            all_dnp_targets.extend(dnp_res["penerima"])

        # 2. Ekstraksi SPP
        all_spp_data = []
        for spp_file in output_pdfs:
            bytes_data = spp_file.read()
            spp_res = extract_spp_data_strict(bytes_data, spp_file.name)
            all_spp_data.append(spp_res)

        # 3. Tampilkan Ringkasan DNP
        st.subheader("📌 Ringkasan Dokumen Input (DNP)")
        st.dataframe(pd.DataFrame(dnp_summary), use_container_width=True)

        # 4. Pencocokan & Analisis Nominal
        st.subheader("📊 Hasil Rekonsiliasi & Analisis Kesesuaian Nilai Bayar")

        status_penerima = []

        for target in all_dnp_targets:
            nama_dnp = target["nama"]
            nominal_dnp = target["nominal"]
            st_dnp = target["st_no"]
            file_dnp = target["dnp_file"]

            if nominal_dnp == 0.0:
                status_penerima.append(
                    {
                        "File DNP": file_dnp,
                        "Nomor ST": st_dnp,
                        "Nama Penerima": nama_dnp,
                        "Tagihan DNP": "Rp 0,00",
                        "Dibayar (SPP)": "Rp 0,00",
                        "Status Pembayaran": "⚪ NIHIL (Rp 0)",
                        "Analisis Nominal": "⚪ TDK MEMERLUKAN SPP",
                        "Bukti SPP": "-",
                    }
                )
                continue

            matching_spp_files = []
            nominal_spp_found = 0.0
            is_nominal_match = False

            for spp in all_spp_data:
                if spp["st_no"].upper() != st_dnp.upper() or spp["st_no"] == "-":
                    continue

                for rec in spp["penerima_records"]:
                    name_ok = is_name_matched(nama_dnp, rec["context_text"])
                    if name_ok:
                        nominal_spp_found = rec["nominal"]
                        # Cek kesesuaian nilai
                        if abs(rec["nominal"] - nominal_dnp) < 1.0:
                            is_nominal_match = True
                            matching_spp_files.append(spp["filename"])
                        else:
                            matching_spp_files.append(
                                f"{spp['filename']} (Beda Nilai)"
                            )

            fmt_dnp = f"Rp {nominal_dnp:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            fmt_spp = (
                f"Rp {nominal_spp_found:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                if nominal_spp_found > 0
                else "-"
            )

            if len(matching_spp_files) > 0 and is_nominal_match:
                status_bayar = "✅ TERBAYARKAN"
                status_analisis = "✅ NOMINAL SESUAI"
            elif len(matching_spp_files) > 0 and not is_nominal_match:
                status_bayar = "⚠️ TERTANGKAP SPP"
                status_analisis = f"⚠️ BEDA NILAI (DNP: {fmt_dnp} vs SPP: {fmt_spp})"
            else:
                status_bayar = "❌ BELUM TERBAYAR"
                status_analisis = "❌ SPP TDK DITEMUKAN"

            status_penerima.append(
                {
                    "File DNP": file_dnp,
                    "Nomor ST": st_dnp,
                    "Nama Penerima": nama_dnp,
                    "Tagihan DNP": fmt_dnp,
                    "Dibayar (SPP)": fmt_spp,
                    "Status Pembayaran": status_bayar,
                    "Analisis Nominal": status_analisis,
                    "Bukti SPP": (
                        ", ".join(matching_spp_files)
                        if matching_spp_files
                        else "-"
                    ),
                }
            )

        df_status = pd.DataFrame(status_penerima)
        st.dataframe(df_status, use_container_width=True)

        # 5. Kesimpulan Detail
        st.subheader("💡 Kesimpulan Analisis Kesesuaian")

        targets_butuh = [r for r in status_penerima if "⚪" not in r["Status Pembayaran"]]
        terbayar_ok = sum(1 for r in targets_butuh if "✅" in r["Status Pembayaran"])
        beda_nominal = sum(1 for r in targets_butuh if "⚠️" in r["Status Pembayaran"])
        belum_bayar = sum(1 for r in targets_butuh if "❌" in r["Status Pembayaran"])

        if terbayar_ok == len(targets_butuh) and len(targets_butuh) > 0:
            st.success(
                f"🎉 **LENGKAP DAN SESUAI!** Seluruh {terbayar_ok} tagihan terbayarkan dengan nominal yang presisi/sesuai."
            )
        else:
            st.warning(
                f"⚠️ **TERDAPAT CATATAN:** {terbayar_ok} Sesuai | {beda_nominal} Beda Nominal | {belum_bayar} Belum Ditemukan SPP."
            )

            st.markdown("**Catatan Rekonsiliasi:**")
            for r in status_penerima:
                if "⚠️" in r["Status Pembayaran"]:
                    st.write(
                        f"- ⚠️ **{r['Nama Penerima']}** [{r['File DNP']}] Terdeteksi di SPP `{r['Bukti SPP']}` tetapi **NOMINAL BEDA** (Tagihan: **{r['Tagihan DNP']}** | Dibayar: **{r['Dibayar (SPP)']}**)."
                    )
                elif "❌" in r["Status Pembayaran"]:
                    st.write(
                        f"- 🔴 **{r['Nama Penerima']}** [{r['File DNP']}] Nominal **{r['Tagihan DNP']}** belum terbayarkan / belum ada SPP."
                    )
                elif "✅" in r["Status Pembayaran"]:
                    st.write(
                        f"- 🟢 **{r['Nama Penerima']}** [{r['File DNP']}] Nominal **{r['Tagihan DNP']}** **LUNAS DAN SESUAI** via `{r['Bukti SPP']}`."
                    )
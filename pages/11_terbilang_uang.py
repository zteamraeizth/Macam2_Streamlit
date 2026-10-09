import streamlit as st


# 1. Fungsi rekursif untuk konversi angka ke kata (Terbilang)
def terbilang(n):
    satuan = [
        "",
        "satu",
        "dua",
        "tiga",
        "empat",
        "lima",
        "enam",
        "tujuh",
        "delapan",
        "sembilan",
        "sepuluh",
        "sebelas",
    ]
    if n < 0:
        return "minus " + terbilang(abs(n))
    elif n == 0:
        return "nol"
    elif n < 12:
        return satuan[n]
    elif n < 20:
        return terbilang(n - 10) + " belas"
    elif n < 100:
        return terbilang(n // 10) + " puluh " + terbilang(n % 10)
    elif n < 200:
        return "seratus " + terbilang(n - 100)
    elif n < 1000:
        return terbilang(n // 10) + " ratus " + terbilang(n % 100)
    elif n < 2000:
        return "seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    elif n < 1000000000000:
        return (
            terbilang(n // 1000000000) + " milyar " + terbilang(n % 1000000000)
        )
    elif n < 1000000000000000:
        return (
            terbilang(n // 1000000000000)
            + " triliun "
            + terbilang(n % 1000000000000)
        )
    else:
        return "Angka terlalu besar"


# 2. Setup Tampilan Streamlit Web
st.set_page_config(
    page_title="Konverter Uang ke Terbilang", page_icon="💵", layout="centered"
)

st.title("💵 Konverter Uang ke Terbilang")
st.write(
    "Masukkan nominal angka untuk mengubahnya menjadi kalimat terbilang Rupiah secara otomatis."
)

st.markdown("---")

# 3. Input Angka
input_angka = st.text_input(
    "Masukkan Nominal Angka:",
    placeholder="Contoh: 1500000 atau 1.500.000",
    key="input_val",
)

# 4. Proses Konversi
raw_input = input_angka.replace(".", "").replace(",", "").strip()

if raw_input:
    try:
        nominal = int(raw_input)

        # Formatting Rupiah
        nominal_fmt = (
            f"Rp {nominal:,.0f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        # Generating Terbilang
        if nominal == 0:
            kalimat = "Nol Rupiah"
        else:
            kalimat = (
                " ".join(terbilang(nominal).split()).title() + " Rupiah"
            )

        st.subheader("Format Rupiah:")
        st.info(f"**{nominal_fmt}**")

        st.subheader("Hasil Terbilang:")

        # Menggunakan st.code agar hasil terbilang langsung memiliki tombol COPY bawaan Streamlit
        st.code(kalimat, language="text")

    except ValueError:
        st.error(
            "⚠️ Format angka tidak valid! Harap masukkan angka tanpa huruf atau karakter khusus."
        )
else:
    st.info("💡 Silakan masukkan nominal angka pada kolom di atas.")
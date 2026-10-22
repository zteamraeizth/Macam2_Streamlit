import os
import platform
import subprocess
import streamlit as st

def convert_docx_to_pdf(input_docx_path: str, output_pdf_path: str) -> bool:
    """
    Mengonversi file DOCX ke PDF.
    - Menggunakan LibreOffice (soffice) untuk Linux / Streamlit Cloud.
    - Menggunakan docx2pdf untuk Windows (lokal).
    
    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    current_os = platform.system()

    try:
        if current_os == "Linux":
            # Folder tujuan output
            output_dir = os.path.dirname(os.path.abspath(output_pdf_path)) or "."
            
            # Eksekusi LibreOffice headless mode
            cmd = [
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                input_docx_path,
                "--outdir", output_dir
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            
            # LibreOffice menghasilkan file dengan nama yang sama dengan docx (ekstensi .pdf)
            base_name = os.path.splitext(os.path.basename(input_docx_path))[0]
            generated_pdf = os.path.join(output_dir, f"{base_name}.pdf")
            
            # Jika nama output_pdf_path beda dari default LibreOffice, lakukan rename
            if generated_pdf != os.path.abspath(output_pdf_path) and os.path.exists(generated_pdf):
                os.replace(generated_pdf, output_pdf_path)

            return True

        elif current_os == "Windows":
            from docx2pdf import convert
            convert(input_docx_path, output_pdf_path)
            return True

        else:
            # macOS atau OS lainnya via LibreOffice
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", input_docx_path], check=True)
            return True

    except subprocess.CalledProcessError as e:
        st.error(f"Gagal mengonversi via LibreOffice: {e.stderr}")
        return False
    except Exception as e:
        st.error(f"Terjadi kesalahan saat konversi PDF: {e}")
        return False

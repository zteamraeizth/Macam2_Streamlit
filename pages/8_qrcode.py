import re
import cv2
import numpy as np
from PIL import Image
import streamlit as st

URL_PATTERN = re.compile(r"^(https?://|www\.)[^\s]+$", re.IGNORECASE)

def is_url(text: str) -> bool:
    return bool(URL_PATTERN.match(text.strip()))

def detect_qr(image_np: np.ndarray):
    detector = cv2.QRCodeDetector()
    retval, decoded_infos, points, _ = detector.detectAndDecodeMulti(image_np)
    
    qr_results = []
    annotated_image = image_np.copy()

    if retval and points is not None:
        for text, pts in zip(decoded_infos, points):
            if not text:
                continue
            
            pts = pts.astype(int)
            cv2.polylines(annotated_image, [pts], True, (0, 255, 0), 3)
            qr_results.append((text, is_url(text)))

    return annotated_image, qr_results

def display_results(qr_results):
    if not qr_results:
        st.warning("Tidak ada QR Code yang terdeteksi.")
        return

    st.subheader("Hasil Deteksi QR Code:")
    for idx, (text, url_flag) in enumerate(qr_results, start=1):
        if url_flag:
            st.success(f"**QR #{idx} (Link Ditemukan)**")
            # st.code menyediakan tombol 'Copy' bawaan di pojok kanan atas box
            st.code(text, language="text")
            st.link_button("Buka Link 🌐", text)
        else:
            st.info(f"**QR #{idx} (Teks Biasa)**")
            st.code(text, language="text")

# --- UI Streamlit ---
st.set_page_config(page_title="QR Code Web Detector", layout="wide")
st.title("🔍 QR Code & Link Web Detector")

mode = st.sidebar.radio("Pilih Mode Input:", ["Upload Gambar / Folder", "Webcam Real-time"])

if mode == "Upload Gambar / Folder":
    uploaded_files = st.file_uploader(
        "Pilih satu atau beberapa file gambar:", 
        type=["jpg", "jpeg", "png", "bmp", "webp"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.divider()
            st.markdown(f"### File: `{uploaded_file.name}`")
            
            image = Image.open(uploaded_file).convert("RGB")
            img_np = np.array(image)
            
            annotated_img, results = detect_qr(img_np)
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(annotated_img, caption="Hasil Deteksi Visual", use_column_width=True)
            with col2:
                display_results(results)

elif mode == "Webcam Real-time":
    camera_image = st.camera_input("Ambil foto dari webcam")
    
    if camera_image:
        image = Image.open(camera_image).convert("RGB")
        img_np = np.array(image)
        
        annotated_img, results = detect_qr(img_np)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(annotated_img, caption="Hasil Scan Webcam", use_column_width=True)
        with col2:
            display_results(results)
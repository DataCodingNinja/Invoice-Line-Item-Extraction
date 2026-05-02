#uses easyOCR + PyMuPDF to render pages
import os
import tempfile
import streamlit as st
import pandas as pd
import easyocr
import fitz  # PyMuPDF
import re

SAMPLE_FOLDER = "sample_invoices"
GT_NAME = "ground_truth.csv"

@st.cache_resource
def get_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = get_reader()

def pdf_to_images_with_pymupdf(path):
    imgs = []
    doc = fitz.open(path)
    for pg in doc:
        mat = fitz.Matrix(2,2)  # zoom for better OCR
        pix = pg.get_pixmap(matrix=mat)
        mode = "RGB" if pix.alpha == 0 else "RGBA"
        img = None
        try:
            from PIL import Image
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            imgs.append(img)
        except:
            pass
    doc.close()
    return imgs

def ocr_image_easyocr(img):
    try:
        import numpy as np
        arr = np.array(img.convert('RGB'))
        result = reader.readtext(arr, detail=0)
        return "\n".join(result)
    except Exception:
        return ""

def read_and_ocr_pdf(path):
    pages = pdf_to_images_with_pymupdf(path)
    texts = []
    for p in pages:
        texts.append(ocr_image_easyocr(p))
    return "\n".join(texts)

def extract_fields_from_text(text):
    t = text.replace("\r", "\n")
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    vendor = lines[0] if lines else ""
    ino = ""
    m = re.search(r"(INV[-\s]?\d+|Invoice\s*No[:#]?\s*([A-Za-z0-9-]+)|Invoice#\s*([A-Za-z0-9-]+))", t, re.I)
    if m:
        ino = m.group(1)
    date = ""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", t)
    if m:
        date = m.group(1)
    else:
        m = re.search(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", t)
        if m:
            date = m.group(1)
    total = ""
    subtotal = ""
    tax = ""
    m = re.search(r"(Total(?:\s*[:\-]?)\s*\$?\s*([0-9\.,]+))", t, re.I)
    if m:
        total = m.group(2)
    if not total:
        nums = re.findall(r"\d{1,3}(?:[,\d]{0,3})?\.\d{2}", t)
        if nums:
            total = nums[-1]
    m = re.search(r"(Subtotal(?:\s*[:\-]?)\s*\$?\s*([0-9\.,]+))", t, re.I)
    if m:
        subtotal = m.group(2)
    m = re.search(r"(Tax(?:\s*[:\-]?)\s*\$?\s*([0-9\.,]+))", t, re.I)
    if m:
        tax = m.group(2)
    line_items = []
    for line in lines:
        m = re.search(r"([A-Za-z0-9 \-]+)\s+(\d+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})", line)
        if m:
            desc = m.group(1).strip()
            qty = int(m.group(2))
            unit = m.group(3).replace(",","")
            ltot = m.group(4).replace(",","")
            line_items.append({"description": desc, "qty": qty, "unit_price": unit, "line_total": ltot})
    return {"vendor": vendor, "invoice_no": ino, "date": date, "subtotal": subtotal, "tax": tax, "total": total, "line_items": line_items}

st.set_page_config(page_title="Invoice OCR (easyOCR + PyMuPDF)", layout="centered")
st.title("Invoice OCR — easyOCR + PyMuPDF (no system Tesseract)")

col1, col2 = st.columns(2)
with col1:
    if st.button("Generate sample invoices (50)"):
        import subprocess, sys
        subprocess.run([sys.executable, "gen_invoices_pdf.py", "--n", "50"])
        st.success("Generated sample_invoices/ with ground_truth.csv")
with col2:
    if st.button("Load ground truth"):
        if os.path.exists(os.path.join(SAMPLE_FOLDER, GT_NAME)):
            df = pd.read_csv(os.path.join(SAMPLE_FOLDER, GT_NAME))
            st.dataframe(df.head())
        else:
            st.warning("No ground_truth.csv found. Generate samples first.")

uploaded = st.file_uploader("Upload invoice PDF files", accept_multiple_files=True, type=["pdf"])
if uploaded:
    results = []
    for f in uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.getbuffer())
            tmp_path = tmp.name
        text = read_and_ocr_pdf(tmp_path)
        try:
            os.unlink(tmp_path)
        except:
            pass
        extracted = extract_fields_from_text(text)
        results.append({"file": f.name, **extracted})
    out_df = pd.DataFrame(results)
    st.write("Extracted fields:")
    st.dataframe(out_df[["file","vendor","invoice_no","date","subtotal","tax","total"]])
    for r in results:
        st.markdown(f"### {r['file']}")
        st.write("Vendor:", r["vendor"])
        st.write("Invoice No:", r["invoice_no"])
        st.write("Date:", r["date"])
        st.write("Subtotal:", r["subtotal"], " Tax:", r["tax"], " Total:", r["total"])
        if r["line_items"]:
            st.write("Line items:")
            st.table(pd.DataFrame(r["line_items"]))
        else:
            st.write("No structured line-items extracted (naive extraction).")

st.markdown("Notes: For better accuracy, preprocess images (grayscale, threshold) or increase zoom in pdf rendering.")

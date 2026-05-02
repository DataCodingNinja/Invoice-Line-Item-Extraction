
# Invoice OCR + Line-item Extraction (easyOCR, PyMuPDF)

Invoice Line Item Extraction — Setup & Notes

Overview
Python project that uses EasyOCR (which depends on PyTorch) to extract line items from invoices.

What
- Proof‑of‑concept that extracts vendor, invoice number, date, subtotal, tax, total, and simple line-items from invoices (PDFs).

Tech
- OCR: easyOCR (no system Tesseract required).
- PDF rendering: PyMuPDF (pymupdf).
- PDF generation (samples): reportlab.

Quick start
1. Create venv and activate:
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate

2. Install dependencies (recommended CPU PyTorch wheel):
   pip install -r requirements.txt
   pip install "torch>=1.12.0" --index-url https://download.pytorch.org/whl/cpu

3. Generate samples:
   python gen_invoices_pdf.py --n 50

4. Run Streamlit app:
   streamlit run app_invoice_easyocr.py

Usage
- Click "Generate sample invoices" or use your PDFs.
- Upload PDFs to extract fields. Results show extracted fields and any found line-items.

Notes & limitations
- Extraction uses heuristics and regexes; not production-grade.
- Improves with image preprocessing, custom regexes, or ML-based table detection.
- Synthetic invoices are clean; real-world invoices vary in layout.


Prerequisites
Windows x64 (you have 64-bit Python).
Python 3.11–3.13 (same interpreter used for installation).
Internet access to install packages.
Important: Install the Microsoft Visual C++ 2015–2022 Redistributable (x64) if not already installed.

python -m pip install --upgrade pip
Install dependencies (CPU-only):

python -m pip install -r requirements.txt --index-url https://download.pytorch.org/whl/cpu
If you require GPU/CUDA support, install the matching torch/torchvision wheels using the appropriate PyTorch index URL for your CUDA version instead of the CPU index URL.
Troubleshooting
WinError 126 (c10.dll) on import:
Install Microsoft Visual C++ 2015–2022 Redistributable (x64) and reboot.
Use the "Dependencies" tool (https://github.com/lucasg/Dependencies) to open:


<python_install_dir>\Lib\site-packages\torch\lib\c10.dll
and identify any missing DLLs. Install any reported runtimes or drivers.
Ensure you installed the correct PyTorch wheel (CPU vs CUDA) that matches your environment.
ModuleNotFoundError: No module named 'torchvision'
Install torchvision with the matching index URL:


python -m pip install torchvision --index-url https://download.pytorch.org/whl/cpu
Verify everything:


python -c "import torch, torchvision, easyocr; print(torch.__version__, torchvision.__version__, easyocr.__version__)"
Notes & Recommendations
Always install torch/torchvision using the PyTorch-provided index URLs to ensure binary compatibility.
Use python -m pip to avoid mismatched pip/python environments.
If you need GPU support, match the CUDA toolkit / driver to the PyTorch wheel; check PyTorch Get Started for the correct command.
Keep the MSVC redistributable and GPU drivers updated.
python -c "import platform, sys; print(platform.architecture(), sys.version)"
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
Any error tracebacks and output of the Dependencies tool listing missing DLLs.

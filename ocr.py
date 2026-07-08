
"""
OCR helpers for the ILM Generator.

Used in two situations:
1. A directly uploaded image file (jpg/jpeg/png) — the whole image is OCR'd.
2. A PDF page that has no real text layer (i.e. a scanned page) — the page
   is rendered to an image first, then OCR'd.

Requires the Tesseract binary to be installed on the host. On Streamlit
Cloud, add a `packages.txt` file to the repo root containing the line:

    tesseract-ocr

so the platform installs it via apt before your app starts.
"""

import io

import pytesseract
from PIL import Image


def ocr_image_bytes(image_bytes):
    """
    Run OCR on raw image bytes (jpg/jpeg/png) and return the extracted text.
    Returns an empty string if OCR fails or finds nothing, rather than
    raising, so a single bad image doesn't crash a multi-file batch.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"[OCR failed for this image: {e}]"


def ocr_pdf_page(page, dpi=200):
    """
    Render a PyMuPDF page to an image and OCR it. Used as a fallback when
    a PDF page's real text layer is empty or nearly empty (a scanned page).
    `page` is a fitz.Page object (from PyMuPDF).
    """
    try:
        import fitz  # local import to avoid a hard dependency if OCR-only use is desired
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        return ocr_image_bytes(img_bytes)
    except Exception as e:
        return f"[OCR failed for this page: {e}]"

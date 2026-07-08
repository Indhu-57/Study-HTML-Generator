"""
Text extraction for the ILM Generator.

Supports: PDF, DOCX, TXT, EPUB, JPG, JPEG, PNG.
DJVU is intentionally not supported — there is no reliable pure-Python
DJVU library, and the djvulibre system binary is not dependably available
on Streamlit Cloud. Convert DJVU files to PDF before uploading.

Scanned (image-only) PDF pages are automatically OCR'd as a fallback
when the page's real text layer is empty or nearly empty.
"""

import io

import fitz  # PyMuPDF
from docx import Document

from ocr import ocr_image_bytes, ocr_pdf_page

SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt", "epub", "jpg", "jpeg", "png"}

# Roughly how many characters make up one printed page of study material.
# Used only to estimate a "page count" for non-PDF formats, where there is
# no real concept of a page (DOCX/TXT/EPUB) or where 1 file = 1 page (images).
_CHARS_PER_PAGE_ESTIMATE = 1800

# A PDF page is treated as "scanned" (no real text layer) if it has fewer
# than this many extracted characters, triggering an OCR fallback for it.
_MIN_CHARS_BEFORE_OCR_FALLBACK = 20


def get_extension(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_supported(filename):
    return get_extension(filename) in SUPPORTED_EXTENSIONS


# -----------------------------------------------------------------
# PDF
# -----------------------------------------------------------------

def extract_pdf_text(file_bytes):
    """
    Extract text from a PDF, one page at a time. Any page with little or
    no real text (a scanned page) is rendered to an image and OCR'd
    automatically. Returns (text, page_count).
    """
    document = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    page_count = len(document)

    for page_number in range(page_count):
        page = document.load_page(page_number)
        page_text = page.get_text().strip()

        if len(page_text) < _MIN_CHARS_BEFORE_OCR_FALLBACK:
            ocr_text = ocr_pdf_page(page)
            if ocr_text:
                page_text = ocr_text

        text += f"\n\n===== PAGE {page_number + 1} =====\n\n"
        text += page_text

    document.close()
    return text, page_count


# -----------------------------------------------------------------
# DOCX
# -----------------------------------------------------------------

def extract_docx_text(file_bytes):
    document = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    text = "\n".join(paragraphs)
    page_count = max(1, len(text) // _CHARS_PER_PAGE_ESTIMATE)
    return text, page_count


# -----------------------------------------------------------------
# TXT
# -----------------------------------------------------------------

def extract_txt_text(file_bytes):
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    page_count = max(1, len(text) // _CHARS_PER_PAGE_ESTIMATE)
    return text, page_count


# -----------------------------------------------------------------
# EPUB
# -----------------------------------------------------------------

def extract_epub_text(file_bytes):
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    tmp_path = "/tmp/_ilm_upload.epub"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    book = epub.read_epub(tmp_path)
    chunks = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            chunk_text = soup.get_text(separator="\n").strip()
            if chunk_text:
                chunks.append(chunk_text)

    text = "\n\n".join(chunks)
    page_count = max(1, len(text) // _CHARS_PER_PAGE_ESTIMATE)
    return text, page_count


# -----------------------------------------------------------------
# IMAGES (jpg / jpeg / png) — OCR only
# -----------------------------------------------------------------

def extract_image_text(file_bytes):
    text = ocr_image_bytes(file_bytes)
    return text, 1  # one image counts as one "page"


# -----------------------------------------------------------------
# DISPATCH
# -----------------------------------------------------------------

def extract_text(file_bytes, filename):
    """
    Extracts text from a single file of any supported type.
    Returns (text, estimated_page_count).
    Raises ValueError for unsupported file types (including .djvu).
    """
    ext = get_extension(filename)

    if ext == "pdf":
        return extract_pdf_text(file_bytes)
    elif ext == "docx":
        return extract_docx_text(file_bytes)
    elif ext == "txt":
        return extract_txt_text(file_bytes)
    elif ext == "epub":
        return extract_epub_text(file_bytes)
    elif ext in ("jpg", "jpeg", "png"):
        return extract_image_text(file_bytes)
    elif ext == "djvu":
        raise ValueError(
            "DJVU files are not supported. Please convert this file to PDF "
            "and upload it again."
        )
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


def extract_multiple(files):
    """
    Extracts and combines text from a list of uploaded files.
    `files` is a list of (filename, file_bytes) tuples.

    Returns a dict:
        {
            "combined_text": str,
            "total_pages": int,
            "per_file": [{"filename": ..., "pages": ..., "chars": ...}, ...],
            "errors": [{"filename": ..., "error": ...}, ...],
        }
    A single failing file does not stop extraction of the others.
    """
    combined_parts = []
    per_file = []
    errors = []
    total_pages = 0

    for filename, file_bytes in files:
        try:
            text, pages = extract_text(file_bytes, filename)
            combined_parts.append(f"\n\n########## SOURCE FILE: {filename} ##########\n\n{text}")
            per_file.append({"filename": filename, "pages": pages, "chars": len(text)})
            total_pages += pages
        except Exception as e:
            errors.append({"filename": filename, "error": str(e)})

    return {
        "combined_text": "\n".join(combined_parts),
        "total_pages": total_pages,
        "per_file": per_file,
        "errors": errors,
    }

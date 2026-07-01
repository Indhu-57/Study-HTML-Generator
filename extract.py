
import fitz  # PyMuPDF


def extract_pdf_text(file_bytes):
    """
    Extract text from a PDF.

    Parameters
    ----------
    file_bytes : bytes
        PDF file in bytes.

    Returns
    -------
    str
        Extracted text from all pages.
    """

    document = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""

    for page_number in range(len(document)):
        page = document.load_page(page_number)
        page_text = page.get_text()

        text += f"\n\n===== PAGE {page_number + 1} =====\n\n"
        text += page_text

    document.close()

    return text

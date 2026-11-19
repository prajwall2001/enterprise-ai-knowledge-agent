
from io import BytesIO
from pypdf import PdfReader


def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF and preserve page numbers.
    """

    reader = PdfReader(BytesIO(pdf_bytes))

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported.")

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        cleaned_text = " ".join(text.split())

        if cleaned_text:
            pages.append({
                "page": page_number,
                "text": cleaned_text
            })

    if not pages:
        raise ValueError("No readable text found in PDF.")

    return pages

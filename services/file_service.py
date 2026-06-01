# file_service.py

import pdfplumber
from PIL import Image
import pytesseract

try:
    import docx
except ImportError:
    docx = None


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file):
    if not docx:
        return ""
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)


def process_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        return extract_text_from_docx(uploaded_file)
    elif file_type in ["png", "jpg", "jpeg"]:
        return extract_text_from_image(uploaded_file)
    else:
        return ""
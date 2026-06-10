from pathlib import Path
from pypdf import PdfReader
from docx import Document

def read_pdf(file_path: str):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def read_docx(file_path: str):
    document = Document(file_path)
    text = []
    for paragraph in document.paragraphs:
        text.append(paragraph.text)
    return "\n".join(text)

def read_txt(file_path: str):
    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()
    
def read_document(file_path: str):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return read_pdf(file_path)
    
    if extension == ".docx":
        return read_docx(file_path)
    
    if extension == ".txt":
        return read_txt(file_path)
    
    raise ValueError(f"Unsupported file type: {extension}")
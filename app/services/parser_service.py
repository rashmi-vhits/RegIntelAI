from pathlib import Path

import fitz
from docx import Document

from app.utils.text import split_into_sections


def parse_document(file_path: str, document_type: str) -> tuple[str, list[dict[str, str]], dict[str, str]]:
    path = Path(file_path)
    if document_type == "pdf":
        text = _extract_pdf_text(path)
    elif document_type == "docx":
        text = _extract_docx_text(path)
    elif document_type == "txt":
        text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        text = ""

    cleaned_text = text.strip()
    sections = split_into_sections(cleaned_text)
    metadata = {
        "file_name": path.name,
        "document_type": document_type,
        "character_count": str(len(cleaned_text)),
        "section_count": str(len(sections)),
    }
    return cleaned_text, sections, metadata


def _extract_pdf_text(path: Path) -> str:
    chunks: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            chunks.append(page.get_text("text"))
    return "\n".join(chunks)


def _extract_docx_text(path: Path) -> str:
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())

from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.report import AnalysisReport
from app.utils.document import detect_document_type, hash_bytes, sanitize_filename
from app.utils.storage import ensure_directories

ALLOWED_TYPES = {"pdf", "docx", "txt"}


async def create_report_from_upload(db: Session, upload: UploadFile) -> AnalysisReport:
    extension = detect_document_type(upload.filename or "")
    if extension not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use pdf, docx, or txt.")

    ensure_directories()

    content = await upload.read()
    safe_name = sanitize_filename(upload.filename or f"document.{extension}")
    file_hash = hash_bytes(content)
    destination = Path(settings.upload_dir) / f"{file_hash}_{safe_name}"
    destination.write_bytes(content)

    report = AnalysisReport(
        original_filename=safe_name,
        stored_file_path=str(destination),
        anonymized_file_path=None,
        document_hash=file_hash,
        document_type=extension,
        status="uploaded",
        audit_log=[
            {
                "action": "upload",
                "message": f"Document uploaded as {safe_name}.",
            }
        ],
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

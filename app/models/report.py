from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    anonymized_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(64), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="uploaded")
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    anonymized_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sections: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    entities: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    completeness: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    classification: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    comparison_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    audit_log: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

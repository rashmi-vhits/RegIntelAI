from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UploadedFileResponse(BaseModel):
    report_id: int
    filename: str
    document_type: str
    status: str


class AnalyzeRequest(BaseModel):
    report_id: int = Field(..., gt=0)


class CompareRequest(BaseModel):
    source_report_id: int = Field(..., gt=0)
    target_report_id: int = Field(..., gt=0)


class SectionOut(BaseModel):
    heading: str
    content: str


class ReportResponse(BaseModel):
    id: int
    original_filename: str
    document_type: str
    status: str
    extracted_text: str
    anonymized_text: str
    sections: list[dict[str, str]]
    entities: dict[str, Any]
    summary: dict[str, Any]
    completeness: dict[str, Any]
    classification: dict[str, Any]
    comparison_snapshot: dict[str, Any]
    audit_log: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompareResponse(BaseModel):
    source_report_id: int
    target_report_id: int
    result: dict[str, Any]

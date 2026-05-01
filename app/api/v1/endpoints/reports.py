from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.report import AnalyzeRequest, CompareRequest, CompareResponse, ReportResponse, UploadedFileResponse
from app.services.analysis_service import analyze_report
from app.services.comparison_service import compare_reports
from app.services.export_service import export_packet_json, export_packet_pdf
from app.services.file_service import create_report_from_upload
from app.services.report_service import get_report_by_id

router = APIRouter()


@router.get("/health")
def api_health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/upload", response_model=UploadedFileResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadedFileResponse:
    report = await create_report_from_upload(db=db, upload=file)
    return UploadedFileResponse(
        report_id=report.id,
        filename=report.original_filename,
        document_type=report.document_type,
        status=report.status,
    )


@router.post("/analyze", response_model=ReportResponse)
def analyze_document(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> ReportResponse:
    report = analyze_report(db=db, report_id=payload.report_id)
    return ReportResponse.model_validate(report)


@router.post("/compare", response_model=CompareResponse)
def compare_document_versions(payload: CompareRequest, db: Session = Depends(get_db)) -> CompareResponse:
    source = get_report_by_id(db, payload.source_report_id)
    target = get_report_by_id(db, payload.target_report_id)
    if source is None or target is None:
        raise HTTPException(status_code=404, detail="One or both reports were not found.")

    result = compare_reports(source, target)
    return CompareResponse(
        source_report_id=payload.source_report_id,
        target_report_id=payload.target_report_id,
        result=result,
    )


@router.get("/report/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    report = get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    return ReportResponse.model_validate(report)


@router.get("/report/{report_id}/export/json")
def export_report_json(report_id: int, compare_to_report_id: int | None = None, db: Session = Depends(get_db)) -> JSONResponse:
    report = get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    comparison_report = get_report_by_id(db, compare_to_report_id) if compare_to_report_id else None
    if compare_to_report_id and comparison_report is None:
        raise HTTPException(status_code=404, detail="Comparison report not found.")

    packet, filename = export_packet_json(report, comparison_report)
    return JSONResponse(content=packet, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/report/{report_id}/export/pdf")
def export_report_pdf(report_id: int, compare_to_report_id: int | None = None, db: Session = Depends(get_db)) -> FileResponse:
    report = get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    comparison_report = get_report_by_id(db, compare_to_report_id) if compare_to_report_id else None
    if compare_to_report_id and comparison_report is None:
        raise HTTPException(status_code=404, detail="Comparison report not found.")

    path, filename = export_packet_pdf(report, comparison_report)
    return FileResponse(path=path, media_type="application/pdf", filename=filename)

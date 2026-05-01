from sqlalchemy.orm import Session

from app.models.report import AnalysisReport


def get_report_by_id(db: Session, report_id: int) -> AnalysisReport | None:
    return db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()

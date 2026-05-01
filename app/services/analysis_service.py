from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.report import AnalysisReport
from app.services.anonymizer_service import anonymize_text
from app.services.classifier_service import classify_sae
from app.services.nlp_service import extract_entities, generate_structured_summary
from app.services.parser_service import parse_document
from app.services.report_service import get_report_by_id
from app.services.review_service import build_review_packet
from app.services.rules_service import evaluate_completeness
from app.utils.form_fields import extract_form_fields


def analyze_report(db: Session, report_id: int) -> AnalysisReport:
    report = get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    extracted_text, sections, metadata = parse_document(report.stored_file_path, report.document_type)
    if not extracted_text:
        raise HTTPException(status_code=400, detail="No text could be extracted from the document.")

    form_fields = extract_form_fields(extracted_text)
    anonymized_text_value, anonymized_file_path, anonymization_info = anonymize_text(report.id, extracted_text)
    entities = extract_entities(extracted_text, form_fields=form_fields)
    summary = generate_structured_summary(anonymized_text_value, entities, sections, form_fields=form_fields)
    completeness = evaluate_completeness(form_fields, sections)
    classification = classify_sae(extracted_text, entities, form_fields)
    review_packet = build_review_packet(form_fields, completeness, classification, anonymization_info)

    report.extracted_text = extracted_text
    report.anonymized_text = anonymized_text_value
    report.anonymized_file_path = anonymized_file_path
    report.sections = sections
    report.entities = {**entities, "form_fields": form_fields}
    report.summary = {
        **summary,
        "parser_metadata": metadata,
        "review_packet": review_packet,
        "anonymization": anonymization_info,
    }
    report.completeness = completeness
    report.classification = classification
    report.comparison_snapshot = {
        "entity_counts": {key: len(value) if isinstance(value, list) else 0 for key, value in entities.items()},
        "current_status": "analyzed",
    }
    report.status = "analyzed"
    report.audit_log = [
        *report.audit_log,
        {
            "action": "analyze",
            "message": "Document parsed, anonymized, summarized, validated, and classified.",
        },
    ]

    db.add(report)
    db.commit()
    db.refresh(report)
    return report

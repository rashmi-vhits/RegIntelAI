from app.models.report import AnalysisReport
from app.services.llm_service import generate_ollama_comparison_summary
from app.utils.form_fields import extract_form_fields
from app.utils.text import normalize_text

FIELD_LABELS = {
    "sae_onset_date": "Onset Date",
    "sae_stop_date": "Stop Date",
    "relationship_of_event_to_intervention": "Relationship",
    "outcome_of_serious_adverse_event": "Outcome",
    "type_of_report": "Report Type",
    "relevant_tests": "Lab Values / Tests",
    "category_of_serious_adverse_event": "Severity Category",
}

FIELD_IMPACTS = {
    "sae_onset_date": "Timeline changed",
    "sae_stop_date": "Resolution window updated",
    "relationship_of_event_to_intervention": "Causality strengthened",
    "outcome_of_serious_adverse_event": "Follow-up clarity improved",
    "type_of_report": "Submission stage advanced",
    "relevant_tests": "Clinical evidence expanded",
    "category_of_serious_adverse_event": "Seriousness interpretation changed",
}

TRACKED_FIELDS = [
    "sae_onset_date",
    "sae_stop_date",
    "relationship_of_event_to_intervention",
    "outcome_of_serious_adverse_event",
    "type_of_report",
    "relevant_tests",
    "category_of_serious_adverse_event",
]


def compare_reports(source: AnalysisReport, target: AnalysisReport) -> dict:
    source_fields = _get_form_fields(source)
    target_fields = _get_form_fields(target)

    changed_fields: list[dict[str, str]] = []
    for field in TRACKED_FIELDS:
        source_value = _stringify(source_fields.get(field))
        target_value = _stringify(target_fields.get(field))
        if normalize_text(source_value) != normalize_text(target_value):
            changed_fields.append(
                {
                    "field": field,
                    "label": FIELD_LABELS.get(field, field.replace("_", " ").title()),
                    "old": source_value or "Missing",
                    "new": target_value or "Missing",
                    "impact": FIELD_IMPACTS.get(field, "Material field updated"),
                }
            )

    source_entities = source.entities or {}
    target_entities = target.entities or {}
    entity_deltas = {}
    for key in sorted(set(source_entities.keys()) | set(target_entities.keys())):
        if key == "form_fields":
            continue
        if source_entities.get(key) != target_entities.get(key):
            entity_deltas[key] = {
                "source": source_entities.get(key),
                "target": target_entities.get(key),
            }

    diff_payload = {
        "source_report_id": source.id,
        "target_report_id": target.id,
        "changed_fields": changed_fields,
        "source_report_type": source_fields.get("type_of_report"),
        "target_report_type": target_fields.get("type_of_report"),
    }

    officer_summary = _build_officer_summary(diff_payload)
    return {
        "has_changes": bool(changed_fields or entity_deltas),
        "change_count": len(changed_fields),
        "summary_banner": f"{len(changed_fields)} material changes detected",
        "changed_fields": changed_fields,
        "entity_deltas": entity_deltas,
        "officer_summary": officer_summary,
    }


def _build_officer_summary(diff_payload: dict) -> dict:
    fallback_lines = []
    for item in diff_payload.get("changed_fields", [])[:5]:
        fallback_lines.append(f"{item['label']} updated from {item['old']} to {item['new']}.")

    fallback = {
        "summary_banner": f"{len(diff_payload.get('changed_fields', []))} material changes detected",
        "officer_summary": " ".join(fallback_lines) or "No material changes detected.",
        "model_provider": "fallback",
    }

    try:
        llm_summary = generate_ollama_comparison_summary(diff_payload)
        return {**fallback, **llm_summary}
    except Exception as exc:
        fallback["llm_error"] = str(exc)
        return fallback


def _stringify(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _get_form_fields(report: AnalysisReport) -> dict:
    if isinstance(report.entities, dict):
        form_fields = report.entities.get("form_fields")
        if isinstance(form_fields, dict) and form_fields:
            return form_fields
    source_text = report.extracted_text or report.anonymized_text or ""
    return extract_form_fields(source_text)

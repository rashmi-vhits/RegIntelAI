from typing import Any


def build_review_packet(
    form_fields: dict[str, Any],
    completeness: dict[str, Any],
    classification: dict[str, Any],
    anonymization: dict[str, Any],
) -> dict[str, Any]:
    missing_fields = completeness.get("missing_fields", [])
    recommended_missing_fields = completeness.get("recommended_missing_fields", [])
    recommendation = build_recommendation(form_fields, completeness, classification)

    return {
        "case_id": form_fields.get("pt_id", "unknown"),
        "severity": classification.get("label", "unknown"),
        "report_type": form_fields.get("type_of_report", "unknown"),
        "missing_fields": missing_fields,
        "recommended_missing_fields": recommended_missing_fields,
        "pii_findings": anonymization.get("matched_patterns", []),
        "recommendation": recommendation,
        "signoff_present": bool(form_fields.get("signature_of_principal_investigator")),
    }


def build_recommendation(
    form_fields: dict[str, Any],
    completeness: dict[str, Any],
    classification: dict[str, Any],
    comparison_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    missing_fields = completeness.get("missing_fields", [])
    severity_label = str(classification.get("label", "unknown")).lower()
    high_severity = severity_label in {
        "death",
        "life-threatening",
        "critical",
        "hospitalization - initial",
        "hospitalization - prolonged",
    }

    status = "Ready for medical review"
    priority = "Medium"
    action = "Continue standard officer review with the available submission record."
    basis: list[str] = []

    if missing_fields and high_severity:
        status = "Escalate for urgent medical review"
        priority = "High"
        action = "Escalate immediately and request missing mandatory fields before case closure."
    elif missing_fields:
        status = "Needs follow-up clarification"
        priority = "Medium"
        action = "Hold for follow-up clarification. Submission is not review-ready due to missing required information."
    elif high_severity:
        status = "Expedited clinical safety review"
        priority = "High"
        action = "Route for expedited clinical safety review based on the serious event category and available details."

    if comparison_result and comparison_result.get("change_count", 0) > 0 and not missing_fields:
        status = "Revised submission ready for continued review"
        priority = "Medium"
        action = "Revised submission resolves key data gaps and is now suitable for continued medical review."

    basis.extend(_field_to_basis_line(field) for field in missing_fields)
    basis.extend(_field_to_basis_line(field, recommended=True) for field in completeness.get("recommended_missing_fields", []))
    if form_fields.get("category_of_serious_adverse_event"):
        basis.append(f"Serious event category: {_titleize(form_fields['category_of_serious_adverse_event'])}")
    if form_fields.get("relationship_of_event_to_intervention"):
        basis.append(f"Relationship to intervention: {form_fields['relationship_of_event_to_intervention'].strip()}")
    if _discontinued_flag(form_fields):
        basis.append("Study intervention was discontinued after the event.")
    if form_fields.get("relevant_tests"):
        basis.append("Supportive treatment and monitoring details were documented.")
    if form_fields.get("outcome_of_serious_adverse_event"):
        basis.append("Follow-up details indicate clinical improvement or updated outcome status.")
    if not form_fields.get("signature_of_principal_investigator"):
        basis.append("Investigator sign-off is not present.")
    if comparison_result and comparison_result.get("change_count", 0) > 0:
        basis.append(f"Version comparison identified {comparison_result['change_count']} material changes.")

    return {
        "status": status,
        "priority": priority,
        "action": action,
        "basis": basis,
    }


def _field_to_basis_line(field: str, recommended: bool = False) -> str:
    label = field.replace("_", " ")
    if recommended:
        return f"Recommended follow-up detail missing: {label}"
    return f"Missing mandatory field: {label}"


def _discontinued_flag(form_fields: dict[str, Any]) -> bool:
    value = str(form_fields.get("study_intervention_discontinued", "")).strip().lower()
    return value == "yes"


def _titleize(value: str) -> str:
    parts = [part.strip() for part in str(value).split("-") if part.strip()]
    return " - ".join(part[:1].upper() + part[1:] for part in parts) if parts else str(value)

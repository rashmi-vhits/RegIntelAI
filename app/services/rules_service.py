from typing import Any

from app.utils.rules import load_rule_pack


def evaluate_completeness(form_fields: dict[str, Any], sections: list[dict[str, str]]) -> dict:
    rule_pack = load_rule_pack("sae_rules.json")
    missing_fields: list[str] = []
    recommended_missing_fields: list[str] = []
    findings: list[dict[str, Any]] = []

    for field in rule_pack.get("required_fields", []):
        if not _has_value(form_fields.get(field)):
            missing_fields.append(field)

    for field in rule_pack.get("recommended_fields", []):
        if not _has_value(form_fields.get(field)):
            recommended_missing_fields.append(field)

    for rule in rule_pack.get("validation_rules", []):
        rule_findings = _evaluate_rule(rule, form_fields)
        findings.extend(rule_findings)
        for finding in rule_findings:
            for field in finding.get("missing_fields", []):
                if field not in missing_fields:
                    missing_fields.append(field)

    if not any("description" in section["heading"].lower() for section in sections):
        findings.append(
            {
                "rule_id": "LOCAL-001",
                "severity": "medium",
                "message": "Descriptive narrative sections are weak or missing.",
                "missing_fields": [],
            }
        )

    score = max(0, 100 - (len(missing_fields) * 12) - (len(findings) * 4))
    return {
        "is_complete": len(missing_fields) == 0,
        "score": score,
        "missing_fields": missing_fields,
        "recommended_missing_fields": recommended_missing_fields,
        "findings": findings,
        "rule_pack": rule_pack.get("rule_pack"),
        "review_recommendation": "manual_review" if missing_fields else "ready_for_officer_review",
    }


def _evaluate_rule(rule: dict[str, Any], form_fields: dict[str, Any]) -> list[dict[str, Any]]:
    check = rule.get("check")
    fields = rule.get("fields", [])

    if check == "required_fields_present":
        missing = [field for field in fields if not _has_value(form_fields.get(field))]
        if missing:
            return [_finding(rule, missing)]
        return []

    if check == "field_required_when":
        condition = rule.get("condition", {})
        condition_value = form_fields.get(condition.get("field", ""))
        allowed_values = condition.get("in", [])
        if condition_value in allowed_values:
            missing = [field for field in fields if not _has_value(form_fields.get(field))]
            if missing:
                return [_finding(rule, missing)]
        return []

    if check == "boolean_like_value_expected":
        missing = [field for field in fields if form_fields.get(field) not in {"Yes", "No"}]
        if missing:
            return [_finding(rule, missing, "Expected Yes/No value.")]
        return []

    return []


def _finding(rule: dict[str, Any], missing_fields: list[str], suffix: str | None = None) -> dict[str, Any]:
    message = f"{rule.get('name')} Missing: {', '.join(missing_fields)}."
    if suffix:
        message = f"{message} {suffix}"
    return {
        "rule_id": rule.get("id"),
        "severity": rule.get("severity"),
        "message": message,
        "missing_fields": missing_fields,
    }


def _has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""

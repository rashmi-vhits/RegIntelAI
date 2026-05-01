import re
from pathlib import Path

from app.core.config import settings
from app.utils.rules import load_rule_pack
from app.utils.storage import ensure_directories

PATTERN_LIBRARY = {
    "patient_name": r"(?im)^(Patient Name:\s*)(.+)$",
    "phone": r"(?im)^(Phone:\s*)(\+?\d[\d -]{8,}\d)$",
    "email": r"(?im)^(Email:\s*)([\w\.-]+@[\w\.-]+\.\w+)$",
    "address": r"(?im)^(Address:\s*)(.+)$",
    "hospital_id": r"(?im)^(Hospital ID:\s*)(.+)$",
    "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
}


def anonymize_text(report_id: int, original_text: str) -> tuple[str, str, dict]:
    ensure_directories()
    anonymized = original_text
    matched_patterns: list[str] = []
    rules = load_rule_pack("anonymization_rules.json")

    for rule in rules.get("rules", []):
        pattern_name = rule.get("pattern")
        expression = PATTERN_LIBRARY.get(pattern_name)
        if not expression:
            continue

        pattern = re.compile(expression)
        replacement = _replacement_for(pattern_name)
        updated_text, count = pattern.subn(replacement, anonymized)
        anonymized = updated_text
        if count:
            matched_patterns.append(pattern_name)

    output_path = Path(settings.anonymized_dir) / f"report_{report_id}_anonymized.txt"
    output_path.write_text(anonymized, encoding="utf-8")
    return anonymized, str(output_path), {
        "rule_pack": rules.get("rule_pack"),
        "matched_patterns": matched_patterns,
        "pii_found": bool(matched_patterns),
    }


def _replacement_for(pattern_name: str) -> str:
    if pattern_name in {"patient_name", "phone", "email", "address", "hospital_id"}:
        return rf"\1[REDACTED_{pattern_name.upper()}]"
    return f"[REDACTED_{pattern_name.upper()}]"

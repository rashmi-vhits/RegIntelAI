import re

from app.services.llm_service import generate_ollama_summary


def extract_entities(text: str, form_fields: dict | None = None) -> dict:
    form_fields = form_fields or {}
    patient_names = sorted(set(re.findall(r"\bpatient(?: name)?[:\- ]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.I)))
    ages = sorted(set(re.findall(r"\bage[:\- ]+(\d{1,3})\b", text, re.I)))
    drug_names = sorted(
        set(re.findall(r"\b(?:drug|medicine|suspect product)[:\- ]+([A-Za-z0-9 \-/]+)", text, re.I))
    )
    events = sorted(set(re.findall(r"\b(?:event|reaction|adverse event)[:\- ]+([A-Za-z0-9 ,\-/]+)", text, re.I)))
    dates = sorted(set(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b", text)))

    if form_fields.get("patient_name") and form_fields["patient_name"] not in patient_names:
        patient_names.append(form_fields["patient_name"])
    if form_fields.get("age") and form_fields["age"] not in ages:
        ages.append(form_fields["age"])
    if form_fields.get("intervention_type"):
        drug_names.append(form_fields["intervention_type"])
    if form_fields.get("adverse_event_terms"):
        events.append(form_fields["adverse_event_terms"])
    if form_fields.get("sae_onset_date"):
        dates.append(form_fields["sae_onset_date"])
    if form_fields.get("sae_stop_date"):
        dates.append(form_fields["sae_stop_date"])

    return {
        "patient_names": sorted(set(patient_names)),
        "ages": sorted(set(ages)),
        "drug_names": sorted(set(item.strip() for item in drug_names if item.strip())),
        "events": sorted(set(item.strip() for item in events if item.strip())),
        "dates": sorted(set(dates)),
    }


def generate_structured_summary(
    text: str,
    entities: dict,
    sections: list[dict[str, str]],
    form_fields: dict | None = None,
) -> dict:
    form_fields = form_fields or {}
    excerpt = text[:700].strip()
    patient = entities["patient_names"][0] if entities["patient_names"] else "Unknown"
    drug = entities["drug_names"][0] if entities["drug_names"] else "Unknown"
    event = entities["events"][0] if entities["events"] else "Unknown"

    fallback_summary = {
        "case_overview": f"Case involves patient {patient}, suspected product {drug}, and event {event}.",
        "narrative_excerpt": excerpt,
        "evidence_snippet": excerpt[:240],
        "officer_note": "Generated using deterministic fallback summary because LLM output was unavailable.",
        "key_entities": entities,
        "section_headings": [section["heading"] for section in sections],
        "confidence": 0.76,
        "model_provider": "fallback",
    }

    try:
        llm_summary = generate_ollama_summary(text=text, entities=entities, form_fields=form_fields)
        return {
            **fallback_summary,
            **llm_summary,
            "key_entities": entities,
            "section_headings": [section["heading"] for section in sections],
        }
    except Exception as exc:
        fallback_summary["llm_error"] = str(exc)
        return fallback_summary

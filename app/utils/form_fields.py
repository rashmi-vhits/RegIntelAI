from typing import Any


MULTILINE_LABELS = {
    "adverse event term(s)": "adverse_event_terms",
    "brief description of participant with no personal identifiers": "participant_description",
    "brief description of the nature of the serious adverse event": "event_description",
    "category of serious adverse event": "category_of_serious_adverse_event",
    "intervention type": "intervention_type",
    "relationship of event to intervention": "relationship_of_event_to_intervention",
    "was study intervention discontinued due to event?": "study_intervention_discontinued",
    "what medications or other steps were taken to treat serious adverse event?": "treatment_steps",
    "list any relevant tests, laboratory data, history, including preexisting medical conditions": "relevant_tests",
    "type of report": "type_of_report",
    "outcome of serious adverse event": "outcome_of_serious_adverse_event",
}

KEY_MAP = {
    "protocol title": "protocol_title",
    "protocol number": "protocol_number",
    "site number": "site_number",
    "pt_id": "pt_id",
    "patient name": "patient_name",
    "age": "age",
    "sex": "sex",
    "phone": "phone",
    "email": "email",
    "address": "address",
    "hospital id": "hospital_id",
    "sae onset date": "sae_onset_date",
    "sae stop date": "sae_stop_date",
    "location of serious adverse event": "sae_location",
    "unexpected adverse event": "unexpected_adverse_event",
    "signature of principal investigator": "signature_of_principal_investigator",
    "date": "date",
    **MULTILINE_LABELS,
}


def extract_form_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    current_key: str | None = None
    buffer: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line:
            label, value = line.split(":", 1)
            normalized_label = KEY_MAP.get(label.strip().lower())
            if normalized_label is not None:
                if current_key is not None:
                    fields[current_key] = "\n".join(buffer).strip()
                    buffer = []
                    current_key = None

                value = value.strip()
                if value:
                    fields[normalized_label] = value
                else:
                    current_key = normalized_label
                continue

        if current_key is not None:
            buffer.append(line)

    if current_key is not None:
        fields[current_key] = "\n".join(buffer).strip()

    return fields

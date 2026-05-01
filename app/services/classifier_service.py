SERIOUSNESS_KEYWORDS = {
    "death": "death",
    "fatal": "death",
    "hospitalized": "hospitalization",
    "hospitalisation": "hospitalization",
    "disability": "permanent impairment / disability",
    "life-threatening": "life-threatening",
    "anaphylaxis": "life-threatening",
    "congenital anomaly": "congenital anomaly / birth defect",
}


def classify_sae(text: str, entities: dict, form_fields: dict) -> dict:
    lower_text = text.lower()
    triggered_rules: list[str] = []
    label = "non-serious"
    confidence = 0.68
    category = str(form_fields.get("category_of_serious_adverse_event", "")).strip()

    if category:
        label = category.lower()
        confidence = 0.93
        triggered_rules.append("Used declared SAE category from source form.")

    for keyword, severity in SERIOUSNESS_KEYWORDS.items():
        if keyword in lower_text and label == "non-serious":
            triggered_rules.append(f"Keyword '{keyword}' matched severity '{severity}'.")
            label = severity
            confidence = 0.88

    if entities.get("events") and label == "non-serious":
        triggered_rules.append("Adverse event present but no high-risk seriousness keyword detected.")

    return {
        "label": label,
        "confidence": confidence,
        "triggered_rules": triggered_rules,
        "explanation": "Rule-first severity classification using form category with keyword fallback.",
    }

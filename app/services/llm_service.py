import json
from typing import Any

from app.core.config import settings

try:
    from ollama import Client
except ImportError:  # pragma: no cover - handled at runtime if dependency is not installed yet
    Client = None


SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "case_overview": {"type": "string"},
        "narrative_excerpt": {"type": "string"},
        "evidence_snippet": {"type": "string"},
        "officer_note": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["case_overview", "narrative_excerpt", "evidence_snippet", "officer_note", "confidence"],
}

COMPARE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary_banner": {"type": "string"},
        "officer_summary": {"type": "string"},
    },
    "required": ["summary_banner", "officer_summary"],
}


def generate_ollama_summary(text: str, entities: dict[str, Any], form_fields: dict[str, Any]) -> dict[str, Any]:
    if settings.llm_provider.lower() != "ollama":
        raise RuntimeError("Ollama provider is not enabled.")
    if Client is None:
        raise RuntimeError("Ollama Python client is not installed.")

    client = Client(host=settings.ollama_base_url, timeout=settings.ollama_timeout)
    prompt = _build_prompt(text=text, entities=entities, form_fields=form_fields)
    response = client.chat(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a regulatory safety review assistant. "
                    "Return concise JSON only. Never include markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        format=SUMMARY_SCHEMA,
        options={"temperature": settings.ollama_temperature},
    )
    content = response["message"]["content"]
    payload = json.loads(content)
    payload["model_provider"] = "ollama"
    payload["model_name"] = settings.llm_model
    return payload


def generate_ollama_comparison_summary(diff_payload: dict[str, Any]) -> dict[str, Any]:
    if settings.llm_provider.lower() != "ollama":
        raise RuntimeError("Ollama provider is not enabled.")
    if Client is None:
        raise RuntimeError("Ollama Python client is not installed.")

    client = Client(host=settings.ollama_base_url, timeout=settings.ollama_timeout)
    response = client.chat(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a regulatory safety review assistant. "
                    "Summarize material changes between report versions for an officer dashboard. "
                    "Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Summarize the important regulatory changes between the initial and revised SAE report.\n"
                    f"Diff payload:\n{json.dumps(diff_payload, indent=2)}"
                ),
            },
        ],
        format=COMPARE_SCHEMA,
        options={"temperature": settings.ollama_temperature},
    )
    payload = json.loads(response["message"]["content"])
    payload["model_provider"] = "ollama"
    payload["model_name"] = settings.llm_model
    return payload


def _build_prompt(text: str, entities: dict[str, Any], form_fields: dict[str, Any]) -> str:
    safe_text = text[:6000]
    return (
        "Summarize this serious adverse event submission for a CDSCO-style officer dashboard.\n"
        "Use the provided entities and form fields to keep the summary factual.\n"
        "Write short, direct output suited for a review screen.\n\n"
        f"Form fields:\n{json.dumps(form_fields, indent=2)}\n\n"
        f"Entities:\n{json.dumps(entities, indent=2)}\n\n"
        f"Document text:\n{safe_text}"
    )

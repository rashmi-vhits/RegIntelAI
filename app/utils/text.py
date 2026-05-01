import re


def split_into_sections(text: str) -> list[dict[str, str]]:
    if not text.strip():
        return []

    lines = [line.strip() for line in text.splitlines()]
    sections: list[dict[str, str]] = []
    current_heading = "General"
    current_content: list[str] = []

    for line in lines:
        if not line:
            continue
        if _looks_like_heading(line):
            if current_content:
                sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})
                current_content = []
            current_heading = line.title()
            continue
        current_content.append(line)

    if current_content:
        sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})

    return sections or [{"heading": "General", "content": text.strip()}]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _looks_like_heading(line: str) -> bool:
    if len(line) > 80:
        return False
    if ":" in line and len(line.split()) <= 6:
        return True
    return line.isupper() and len(line.split()) <= 8

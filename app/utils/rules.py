import json
from functools import lru_cache
from pathlib import Path
from typing import Any


RULES_DIR = Path("data/rules")


@lru_cache(maxsize=16)
def load_rule_pack(filename: str) -> dict[str, Any]:
    path = RULES_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

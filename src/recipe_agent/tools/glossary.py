from __future__ import annotations

import json
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

_TERMS_PATH = Path(__file__).resolve().parents[1] / "glossary" / "terms.toml"


@lru_cache(maxsize=1)
def _load_terms() -> dict[str, dict[str, Any]]:
    with _TERMS_PATH.open("rb") as file:
        data = tomllib.load(file)
    return data.get("terms", {})


def _normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _term_payload(term: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "term": term,
        "definition": entry.get("definition", ""),
        "aliases": entry.get("aliases", []),
        "category": entry.get("category", "uncategorized"),
    }


def lookup_domain_term(term: str) -> str:
    """Look up a validated semiconductor recipe domain term or alias."""
    normalized = _normalize(term)
    for key, entry in _load_terms().items():
        aliases = [_normalize(str(alias)) for alias in entry.get("aliases", [])]
        if normalized == _normalize(key) or normalized in aliases:
            return json.dumps(_term_payload(key, entry), ensure_ascii=False, indent=2)
    return f"No glossary entry found for {term!r}."


def list_domain_terms(prefix: str = "", category: str | None = None) -> str:
    """List validated semiconductor recipe glossary terms."""
    normalized_prefix = _normalize(prefix) if prefix else ""
    normalized_category = _normalize(category) if category else ""

    terms = []
    for key, entry in sorted(_load_terms().items()):
        if normalized_prefix and not _normalize(key).startswith(normalized_prefix):
            continue
        entry_category = _normalize(str(entry.get("category", "")))
        if normalized_category and entry_category != normalized_category:
            continue
        terms.append(_term_payload(key, entry))

    return json.dumps(terms, ensure_ascii=False, indent=2)

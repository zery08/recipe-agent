from __future__ import annotations

import json

_GLOSSARY: dict[str, dict[str, object]] = {
    "conversion_rate": {
        "definition": "conversions / clicks for a recipe or recipe cohort.",
        "aliases": ["CVR", "전환율"],
    },
    "recipe_view": {
        "definition": "A user-visible impression or detail-page view for a recipe.",
        "aliases": ["조회", "레시피 조회"],
    },
    "ingredient_cost": {
        "definition": "Estimated ingredient-only cost, excluding labor and overhead.",
        "aliases": ["재료비"],
    },
}


def lookup_domain_term(term: str) -> str:
    """Look up a recipe analytics domain term or alias."""
    normalized = term.strip().lower()
    for key, entry in _GLOSSARY.items():
        aliases = [str(alias).lower() for alias in entry.get("aliases", [])]
        if normalized == key.lower() or normalized in aliases:
            payload = {"term": key, **entry}
            return json.dumps(payload, ensure_ascii=False, indent=2)
    return f"No glossary entry found for {term!r}."


def list_domain_terms(prefix: str = "") -> str:
    """List known recipe analytics glossary terms."""
    normalized = prefix.strip().lower()
    terms = sorted(term for term in _GLOSSARY if not normalized or term.startswith(normalized))
    return json.dumps(terms, ensure_ascii=False, indent=2)


def create_domain_term(term: str, definition: str, aliases: list[str] | None = None) -> str:
    """Create or update an in-memory domain glossary entry for this process."""
    normalized = term.strip().lower().replace(" ", "_")
    if not normalized:
        raise ValueError("term is required.")
    if not definition.strip():
        raise ValueError("definition is required.")

    _GLOSSARY[normalized] = {
        "definition": definition.strip(),
        "aliases": aliases or [],
    }
    return json.dumps({"term": normalized, **_GLOSSARY[normalized]}, ensure_ascii=False, indent=2)

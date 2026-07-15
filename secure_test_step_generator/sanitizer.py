"""Sanitization stage: raw text -> (sanitized text, SanitizationReport).

This is the security boundary the Architect approved: nothing from
document_reader.py / ocr.py may reach llm_provider.py without going
through sanitize_text() first. See models.py's docstring for how the
type system enforces this at the pipeline level.
"""
from .models import SanitizationReport
from .patterns import (
    ALL_PATTERNS,
    INJECTION_PATTERNS,
    known_internal_terms_pattern,
    mask_person_names,
)


def sanitize_text(text: str) -> tuple[str, SanitizationReport]:
    """Replace every sensitive match with its category placeholder.
    Never deletes -- always substitutes, so sanitized text stays
    readable to both the LLM and a human reviewing the report.

    Also neutralizes prompt-injection-shaped phrasing (see
    patterns.INJECTION_PATTERNS) -- OCR text and tester notes are
    untrusted input the same way PII is, so they go through the same
    substitute-never-delete treatment before reaching the LLM.
    """
    if not text:
        return text, SanitizationReport()

    sanitized = text
    counts: dict[str, int] = {}

    for pattern in ALL_PATTERNS + INJECTION_PATTERNS:
        sanitized, n = pattern.regex.subn(pattern.placeholder, sanitized)
        if n:
            counts[pattern.category] = counts.get(pattern.category, 0) + n

    sanitized, n = mask_person_names(sanitized)
    if n:
        counts["person_name"] = counts.get("person_name", 0) + n

    internal_terms_regex = known_internal_terms_pattern()
    if internal_terms_regex is not None:
        sanitized, n = internal_terms_regex.subn("<INTERNAL_TERM>", sanitized)
        if n:
            counts["internal_term"] = counts.get("internal_term", 0) + n

    return sanitized, SanitizationReport(counts_by_category=counts)

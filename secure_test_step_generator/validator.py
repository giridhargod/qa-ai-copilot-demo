"""Validation stage: the last checkpoint before Excel export.

Two responsibilities:
1. Flag steps that are too thin to trust as-is (missing action/expected
   result, or a low confidence score with no stated reason) so a human
   reviewer's attention goes to the right rows.
2. Defense-in-depth re-sanitization: re-run the same sanitizer used on
   the evidence against the AI's own output text. The LLM only ever
   sees sanitized evidence, so it structurally can't repeat something
   it was never shown -- but this catches the case where sanitization
   upstream missed a pattern in the original OCR text, so the same
   gap doesn't silently reach the Excel file untouched.
"""
from dataclasses import replace

from . import config
from .models import TestStep
from .sanitizer import sanitize_text


def validate_steps(steps: list[TestStep]) -> list[TestStep]:
    return [_validate_one(step) for step in steps]


def _validate_one(step: TestStep) -> TestStep:
    warnings = list(step.warnings)
    action = step.action
    expected_result = step.expected_result
    confidence_reason = step.confidence_reason

    if not action.strip() or not expected_result.strip():
        warnings.append(
            "Action or Expected Result is empty -- requires manual authoring."
        )

    if step.confidence < config.LOW_CONFIDENCE_THRESHOLD and not confidence_reason.strip():
        warnings.append(
            "Low confidence with no reason given by the AI -- review manually."
        )

    action, action_report = sanitize_text(action)
    expected_result, expected_report = sanitize_text(expected_result)
    confidence_reason, reason_report = sanitize_text(confidence_reason)

    leaked_total = action_report.total + expected_report.total + reason_report.total
    if leaked_total:
        warnings.append(
            f"Potential sensitive data found in AI output and redacted "
            f"({leaked_total} match(es)) -- verify upstream sanitization coverage."
        )

    return replace(
        step,
        action=action,
        expected_result=expected_result,
        confidence_reason=confidence_reason,
        warnings=warnings,
    )

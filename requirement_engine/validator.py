#requirement_engine/validator.py
"""
Requirement Validation Engine

Purpose
-------
Validates extracted requirements before AI-based processing.

This module performs deterministic QA validation to identify
common requirement quality issues.

Author:
QA AI Copilot
"""

from typing import List


class RequirementValidator:

    """
    Performs deterministic validation on requirements.
    """

    MANDATORY_WORDS = [
        "shall",
        "must",
        "should"
    ]

    @classmethod
    def validate(
        cls,
        requirements: List[dict]
    ) -> List[dict]:

        validated = []

        for requirement in requirements:

            issues = []

            text = requirement["text"].lower()

            # -------------------------
            # Check 1
            # Requirement wording
            # -------------------------

            if not any(
                word in text
                for word in cls.MANDATORY_WORDS
            ):
                issues.append(
                    "Requirement is not testable. Missing mandatory wording."
                )

            # -------------------------
            # Check 2
            # Very short requirement
            # -------------------------

            if len(text.split()) < 4:

                issues.append(
                    "Requirement is too short."
                )

            # -------------------------
            # Check 3
            # Ends properly
            # -------------------------

            if not requirement["text"].strip().endswith("."):

                issues.append(
                    "Requirement should end with a period."
                )

            requirement["validation"] = {
                "passed": len(issues) == 0,
                "issues": issues
            }

            validated.append(
                requirement
            )

        return validated
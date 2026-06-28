#requirement_engine/classifier.py
"""
Requirement Classifier

Purpose
-------
Classifies extracted requirements into enterprise QA categories.

This module uses deterministic rules only.
No AI reasoning should occur here.

Future Enhancements
-------------------
- Multi-label classification
- AI-assisted classification
- Custom organization-specific categories
"""

from typing import Dict


class RequirementClassifier:

    CATEGORY_KEYWORDS = {
        "Functional": [
            "create",
            "update",
            "delete",
            "edit",
            "view",
            "search",
            "filter",
            "login",
            "logout"
        ],

        "Validation": [
            "mandatory",
            "required",
            "unique",
            "validation",
            "duplicate",
            "exactly",
            "must"
        ],

        "Security": [
            "authentication",
            "authorization",
            "unauthorized",
            "permission",
            "access",
            "session",
            "encrypt",
            "mask",
            "pii"
        ],

        "Performance": [
            "seconds",
            "performance",
            "response",
            "load",
            "concurrent",
            "throughput"
        ],

        "Accessibility": [
            "keyboard",
            "screen reader",
            "accessibility",
            "wcag"
        ],

        "UI": [
            "screen",
            "page",
            "button",
            "field",
            "dropdown",
            "textbox"
        ],

        "API": [
            "api",
            "endpoint",
            "request",
            "response"
        ],

        "Database": [
            "database",
            "table",
            "column",
            "record"
        ],

        "Integration": [
            "integration",
            "external",
            "third-party",
            "service"
        ]
    }

    DEFAULT_CATEGORY = "General"

    @classmethod
    def classify(
        cls,
        requirement: Dict
    ) -> Dict:

        text = requirement.get(
            "text",
            ""
        ).lower()

        category = cls.DEFAULT_CATEGORY

        for candidate, keywords in cls.CATEGORY_KEYWORDS.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                category = candidate
                break

        requirement["category"] = category

        return requirement
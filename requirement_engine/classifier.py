# requirement_engine/classifier.py
"""
Requirement Classifier

Purpose
-------
Classifies extracted requirements into enterprise QA categories.

This module performs deterministic classification only.
No AI reasoning should occur here.

Future Enhancements
-------------------
- Multi-label classification
- AI-assisted classification
- Organization-specific rule packs
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
            "logout",
            "register",
            "submit"
        ],

        "Validation": [
            "mandatory",
            "required",
            "unique",
            "validation",
            "duplicate",
            "exactly",
            "minimum",
            "maximum",
            "at least",
            "must contain",
            "length",
            "format"
        ],

        "Security": [
            "authentication",
            "authorization",
            "permission",
            "access",
            "session",
            "encrypt",
            "mask",
            "password",
            "account lock",
            "lock",
            "failed attempts",
            "mfa",
            "otp",
            "oauth",
            "sso",
            "fingerprint",
            "biometric",
            "pii"
        ],

        "Performance": [
            "response",
            "response time",
            "seconds",
            "latency",
            "load",
            "throughput",
            "concurrent"
        ],

        "Accessibility": [
            "keyboard",
            "screen reader",
            "wcag",
            "accessibility"
        ],

        "UI": [
            "screen",
            "page",
            "button",
            "field",
            "textbox",
            "dropdown"
        ],

        "API": [
            "api",
            "endpoint",
            "request",
            "response body"
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

        for category, keywords in cls.CATEGORY_KEYWORDS.items():

            if any(
                keyword in text
                for keyword in keywords
            ):

                requirement["category"] = category
                return requirement

        requirement["category"] = cls.DEFAULT_CATEGORY

        return requirement
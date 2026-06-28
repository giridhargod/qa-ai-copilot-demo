#requirement_engine/quality.py
"""
Requirement Quality Scoring Engine

Purpose
-------
Calculates quality scores for extracted requirements.

The score helps determine whether requirements are
ready for downstream QA activities.

Author:
QA AI Copilot
"""

from typing import List


class RequirementQualityScorer:

    """
    Calculates requirement readiness metrics.
    """

    @classmethod
    def evaluate(
        cls,
        requirements: List[dict]
    ) -> dict:

        total = len(requirements)

        passed = 0
        failed = 0

        issue_count = 0

        category_distribution = {}

        for req in requirements:

            category = req.get(
                "category",
                "Unknown"
            )

            category_distribution[category] = (
                category_distribution.get(
                    category,
                    0
                ) + 1
            )

            validation = req.get(
                "validation",
                {}
            )

            if validation.get("passed"):

                passed += 1

            else:

                failed += 1

                issue_count += len(
                    validation.get(
                        "issues",
                        []
                    )
                )

        readiness_score = 100

        if total:

            readiness_score = round(
                (passed / total) * 100,
                2
            )

        return {

            "overall_score": readiness_score,

            "total_requirements": total,

            "passed": passed,

            "failed": failed,

            "issues_found": issue_count,

            "category_distribution":
            category_distribution,

            "status": (
                "READY"
                if readiness_score >= 90
                else
                "SME REVIEW REQUIRED"
            )
        }
# requirement_engine/quality.py
"""
Requirement Quality Scoring Engine
"""

from typing import List


class RequirementQualityScorer:

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

        needs_sme = False

        for requirement in requirements:

            category = requirement.get(
                "category",
                "Unknown"
            )

            category_distribution[category] = (

                category_distribution.get(
                    category,
                    0
                ) + 1

            )

            validation = requirement.get(
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

            if requirement.get(
                "review",
                {}
            ).get(
                "needs_sme",
                False
            ):

                needs_sme = True

        readiness_score = 100

        if total:

            readiness_score = round(

                (passed / total) * 100,

                2
            )

        if failed > 0:

            status = "NOT READY"

        elif needs_sme:

            status = "READY WITH SME REVIEW"

        else:

            status = "READY"

        return {

            "overall_score": readiness_score,

            "total_requirements": total,

            "passed": passed,

            "failed": failed,

            "issues_found": issue_count,

            "category_distribution":
                category_distribution,

            "needs_sme": needs_sme,

            "status": status
        }
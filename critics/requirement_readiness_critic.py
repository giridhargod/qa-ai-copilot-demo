# critics/requirement_readiness_critic.py
from critics.base_critic import BaseCritic

class RequirementReadinessCritic:
    """
    Reviews the Requirement Readiness output before
    allowing the workflow to continue.

    The critic never invents requirements.

    It evaluates confidence,
    consistency,
    ambiguity,
    and recommendation quality.
    """

    @staticmethod
    def review(
        quality_report: dict,
        requirements: list
    ) -> dict:

        observations = []

        confidence = 100

        if quality_report["failed"] > 0:

            observations.append(
                "Some requirements failed readiness validation."
            )

            confidence -= 20

        if quality_report["issues_found"] > 5:

            observations.append(
                "Large number of requirement issues detected."
            )

            confidence -= 20

        needs_sme = any(

            req["review"]["needs_sme"]

            for req in requirements
        )

        if needs_sme:

            observations.append(
                "SME clarification recommended."
            )

            confidence -= 15

        return {

            "confidence": max(confidence, 0),

            "approved": confidence >= 80,

            "observations": observations
        }

    @property
    def name(self) -> str:
        return "RequirementReadinessCritic"

    def review(
        self,
        result: dict
    ) -> dict:

        quality = result.get("quality", {})

        score = quality.get("overall_score", 0)

        failed = quality.get("failed", 0)

        issues = quality.get("issues_found", 0)

        status = quality.get(
            "status",
            "UNKNOWN"
        )

        confidence = 100

        warnings = []

        recommendations = []

        reasoning = []

        # -------------------------
        # Rule 1
        # -------------------------

        if failed > 0:

            confidence -= failed * 5

            warnings.append(
                f"{failed} requirement(s) failed validation."
            )

        # -------------------------
        # Rule 2
        # -------------------------

        if issues > 0:

            confidence -= issues * 2

            warnings.append(
                f"{issues} issue(s) detected."
            )

        # -------------------------
        # Rule 3
        # -------------------------

        if score < 70:

            confidence -= 5

            recommendations.append(
                "Requirement quality is below enterprise threshold."
            )

        # -------------------------
        # Rule 4
        # -------------------------

        needs_sme = status != "READY"

        if needs_sme:

            recommendations.append(
                "SME review is recommended before continuing."
            )

            reasoning.append(
                "Workflow confidence is below the release threshold."
            )

        else:

            reasoning.append(
                "Requirement quality satisfies enterprise readiness."
            )

        confidence = max(
            0,
            min(confidence, 100)
        )

        approved = (

            confidence >= 80

            and

            not needs_sme
        )

        return {

            "approved": approved,

            "confidence": confidence,

            "needs_sme": needs_sme,

            "warnings": warnings,

            "recommendations": recommendations,

            "reasoning": reasoning
        }
# critics/requirement_readiness_critic.py
from critics.base_critic import BaseCritic

class RequirementReadinessCritic(BaseCritic):
    """
    Enterprise Requirement Readiness Critic.

    Responsibilities
    ----------------
    • Review Requirement Readiness output.
    • Evaluate confidence.
    • Recommend SME escalation when required.
    • Never modify requirements.
    • Never invent requirements.
    """

    @property
    def name(self) -> str:
        return "RequirementReadinessCritic"

    def review(
        self,
        quality_report: dict,
        requirements: list
    ) -> dict:

        confidence = 100

        warnings = []

        recommendations = []

        reasoning = []

        failed = quality_report.get("failed", 0)

        issues = quality_report.get("issues_found", 0)

        overall_score = quality_report.get(
            "overall_score",
            0
        )

        status = quality_report.get(
            "status",
            "UNKNOWN"
        )

        # ----------------------------------
        # Rule 1
        # Failed Requirements
        # ----------------------------------

        if failed > 0:

            confidence -= failed * 5

            warnings.append(
                f"{failed} requirement(s) failed validation."
            )

        # ----------------------------------
        # Rule 2
        # Requirement Issues
        # ----------------------------------

        if issues > 0:

            confidence -= issues * 2

            warnings.append(
                f"{issues} issue(s) detected."
            )

        # ----------------------------------
        # Rule 3
        # Enterprise Threshold
        # ----------------------------------

        if overall_score < 70:

            confidence -= 10

            recommendations.append(
                "Requirement quality is below enterprise threshold."
            )

        # ----------------------------------
        # Rule 4
        # SME Escalation
        # ----------------------------------

        needs_sme = any(

            requirement.get(
                "review",
                {}
            ).get(
                "needs_sme",
                False
            )

            for requirement in requirements
        )

        if needs_sme:

            confidence -= 10

            recommendations.append(
                "SME review is recommended before workflow execution."
            )

            reasoning.append(
                "Business clarification is required."
            )

        else:

            reasoning.append(
                "Requirement Readiness satisfies enterprise quality standards."
            )

        confidence = max(
            0,
            min(confidence, 100)
        )

        approved = (

            confidence >= 80

            and

            status == "READY"
        )

        return {

            "approved": approved,

            "confidence": confidence,

            "needs_sme": needs_sme,

            "warnings": warnings,

            "recommendations": recommendations,

            "reasoning": reasoning
        }
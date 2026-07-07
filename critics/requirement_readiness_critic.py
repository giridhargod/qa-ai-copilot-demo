# critics/requirement_readiness_critic.py
from critics.base_critic import BaseCritic
from governance.contracts import GateDecision
from governance.status import WorkflowStatus

# Enterprise thresholds for translating this Critic's verdict into a
# workflow-control decision. These are business thresholds, owned by
# this Critic (not Governance) — tune here, not in governance/.
HARD_FAIL_CONFIDENCE = 40


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

    @staticmethod
    def to_gate_decision(review_result: dict) -> GateDecision:
        """
        Translates this Critic's verdict into the neutral GateDecision
        contract Governance understands. This is where the business
        interpretation of "approved"/"confidence"/"needs_sme" lives —
        Governance never inspects these fields itself.
        """

        confidence = review_result.get("confidence", 0)
        approved = review_result.get("approved", False)
        needs_sme = review_result.get("needs_sme", False)

        if needs_sme:
            return GateDecision(
                proceed=False,
                status=WorkflowStatus.NEEDS_SME,
                reason=(
                    "Requirement Readiness Critic flagged SME review "
                    "as required before proceeding."
                ),
            )

        if approved:
            return GateDecision(
                proceed=True,
                status=WorkflowStatus.RUNNING,
            )

        if confidence < HARD_FAIL_CONFIDENCE:
            return GateDecision(
                proceed=False,
                status=WorkflowStatus.FAILED_VALIDATION,
                reason=(
                    f"Requirement Readiness confidence ({confidence}) is "
                    f"below the enterprise floor ({HARD_FAIL_CONFIDENCE})."
                ),
            )

        return GateDecision(
            proceed=False,
            status=WorkflowStatus.PAUSED_FOR_REVIEW,
            reason=(
                f"Requirement Readiness confidence ({confidence}) is "
                "below the enterprise approval threshold."
            ),
        )
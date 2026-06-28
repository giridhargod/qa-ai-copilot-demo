#services/readiness_service.py
from requirement_engine.extractor import RequirementExtractor
from requirement_engine.classifier import RequirementClassifier
from requirement_engine.validator import RequirementValidator
from requirement_engine.reviewer import RequirementReviewer
from requirement_engine.quality import RequirementQualityScorer


class ReadinessService:
    """
    Enterprise Requirement Readiness Service.

    Executes the complete deterministic Requirement
    Readiness pipeline before AI agents continue.

    Pipeline:

    Extract
        ↓
    Classify
        ↓
    Validate
        ↓
    Review
        ↓
    Score
    """

    @staticmethod
    def analyze(document: str) -> dict:

        # -------------------------
        # Extract
        # -------------------------
        requirements = RequirementExtractor.extract(
            document
        )

        # -------------------------
        # Classify
        # -------------------------
        requirements = [

            RequirementClassifier.classify(req)

            for req in requirements
        ]

        # -------------------------
        # Validate
        # -------------------------
        requirements = RequirementValidator.validate(
            requirements
        )

        # -------------------------
        # Review
        # -------------------------
        requirements = RequirementReviewer.review(
            requirements
        )

        # -------------------------
        # Score
        # -------------------------
        quality_report = RequirementQualityScorer.evaluate(
            requirements
        )

        critic = RequirementReadinessCritic.review(
            quality_report,
            requirements
        )

        return {

    "requirements": requirements,

    "quality": quality_report,

    "review": {

        "status": quality_report["status"],

        "overall_score": quality_report["overall_score"],

        "total_requirements":
            quality_report["total_requirements"],

        "passed":
            quality_report["passed"],

        "failed":
            quality_report["failed"],

        "issues_found":
            quality_report["issues_found"],

        "category_distribution":
            quality_report["category_distribution"]

        "critic": critic    
    }
}
    from critics.requirement_readiness_critic import (
    RequirementReadinessCritic
)
#services/readiness_service.py
from critics.requirement_readiness_critic import (
    RequirementReadinessCritic
)

from requirement_engine.extractor import (
    RequirementExtractor
)

from requirement_engine.classifier import (
    RequirementClassifier
)

from requirement_engine.validator import (
    RequirementValidator
)

from requirement_engine.reviewer import (
    RequirementReviewer
)

from requirement_engine.quality import (
    RequirementQualityScorer
)


class ReadinessService:
    """
    Enterprise Requirement Readiness Service.

    Executes the complete deterministic
    Requirement Readiness pipeline.

    Pipeline
    --------

    Extract
        ↓
    Classify
        ↓
    Validate
        ↓
    Review
        ↓
    Quality Score
        ↓
    Requirement Readiness Critic
    """

    @staticmethod
    def analyze(
        document: str
    ) -> dict:

        # ---------------------------------
        # Step 1
        # Extract
        # ---------------------------------

        requirements = RequirementExtractor.extract(
            document
        )

        # ---------------------------------
        # Step 2
        # Classify
        # ---------------------------------

        requirements = [

            RequirementClassifier.classify(
                requirement
            )

            for requirement in requirements
        ]

        # ---------------------------------
        # Step 3
        # Validate
        # ---------------------------------

        requirements = RequirementValidator.validate(
            requirements
        )

        # ---------------------------------
        # Step 4
        # Review
        # ---------------------------------

        requirements = RequirementReviewer.review(
            requirements
        )

        # ---------------------------------
        # Step 5
        # Quality
        # ---------------------------------

        quality_report = (
            RequirementQualityScorer.evaluate(
                requirements
            )
        )

        # ---------------------------------
        # Step 6
        # Critic
        # ---------------------------------

        critic = RequirementReadinessCritic()

        critic_report = critic.review(

            quality_report,

            requirements
        )

        # ---------------------------------
        # Final Response
        # ---------------------------------

        return {

            "requirements": requirements,

            "quality": quality_report,

            "review": {

                "status":
                    quality_report["status"],

                "overall_score":
                    quality_report["overall_score"],

                "total_requirements":
                    quality_report["total_requirements"],

                "passed":
                    quality_report["passed"],

                "failed":
                    quality_report["failed"],

                "issues_found":
                    quality_report["issues_found"],

                "category_distribution":
                    quality_report[
                        "category_distribution"
                    ]
            },

            "critic": critic_report
        }
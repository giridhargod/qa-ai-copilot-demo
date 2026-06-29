# agents/requirement_readiness_agent.py
from agents.base_agent import BaseAgent

from models.workflow_state import WorkflowState

from services.readiness_service import ReadinessService


class RequirementReadinessAgent(BaseAgent):
    """
    Enterprise Requirement Readiness Agent.

    Executes the Requirement Readiness pipeline and
    stores the results inside WorkflowState.

    This agent performs deterministic validation
    before AI-dependent workflow stages begin.
    """

    @property
    def name(self) -> str:
        return "RequirementReadinessAgent"

    def execute(
        self,
        state: WorkflowState
    ) -> WorkflowState:

        readiness_result = ReadinessService.analyze(
            state.sanitized_input
        )

        state.requirements = readiness_result[
            "requirements"
        ]

        state.requirement_quality = readiness_result[
            "quality"
        ]

        state.requirement_review = readiness_result[
            "review"
        ]

        state.critic_review = readiness_result[
            "critic"
        ]

        return state
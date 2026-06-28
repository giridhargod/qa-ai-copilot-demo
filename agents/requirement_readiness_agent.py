#agents/requirement_readiness_agent.py
from agents.base_agent import BaseAgent
from models.workflow_state import WorkflowState
from services.readiness_service import ReadinessService


class RequirementReadinessAgent(BaseAgent):

    @property
    def name(self):

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
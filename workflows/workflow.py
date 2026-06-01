from agents import (
    UIAnalysisAgent,
    ImpactAnalysisAgent,
    TestcaseGenerationAgent,
    CriticAgent
)

from models import WorkflowState
from services import OpenAIService

from services.pii_service import process_pii


class WorkflowOrchestrator:

    def __init__(self):

        llm_service = OpenAIService()

        self.agents = [
            UIAnalysisAgent(llm_service),
            ImpactAnalysisAgent(llm_service),
            TestcaseGenerationAgent(llm_service),
            CriticAgent(llm_service)
        ]

    def run(
        self,
        user_input: str
    ) -> WorkflowState:

        state = WorkflowState()

        state.raw_input = user_input

        pii_result = process_pii(user_input)

        state.pii_report = pii_result

        state.sanitized_input = pii_result.get(
            "sanitized",
            user_input
        )

        for agent in self.agents:

            state = agent.execute(state)

        return state
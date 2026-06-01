from agents.base_agent import BaseAgent
from agents.prompts import IMPACT_AGENT_PROMPT
from models.workflow_state import WorkflowState


class ImpactAnalysisAgent(BaseAgent):

    def __init__(self, llm_service):
        self.llm_service = llm_service

    @property
    def name(self):
        return "ImpactAnalysisAgent"

    def execute(
        self,
        state: WorkflowState
    ) -> WorkflowState:

        prompt = f"""
{IMPACT_AGENT_PROMPT}

Input:
{state.sanitized_input}
"""

        result = self.llm_service.generate(prompt)

        state.impact_analysis = result

        return state
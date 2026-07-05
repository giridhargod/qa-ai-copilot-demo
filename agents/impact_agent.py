#agents/impact_agent.py
from agents.base_agent import LLMAgent
from agents.prompts import IMPACT_AGENT_PROMPT
from models.workflow_state import WorkflowState


class ImpactAnalysisAgent(LLMAgent):

    prompt_template = IMPACT_AGENT_PROMPT

    @property
    def name(self):
        return "ImpactAnalysisAgent"

    def get_input(self, state: WorkflowState):
        return state.sanitized_input

    def store_result(self, state: WorkflowState, result):
        state.impact_analysis = result

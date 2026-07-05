#agents/ui_agent.py
from agents.base_agent import LLMAgent
from agents.prompts import UI_AGENT_PROMPT
from models.workflow_state import WorkflowState


class UIAnalysisAgent(LLMAgent):

    prompt_template = UI_AGENT_PROMPT

    @property
    def name(self):
        return "UIAnalysisAgent"

    def get_input(self, state: WorkflowState):
        return state.sanitized_input

    def store_result(self, state: WorkflowState, result):
        state.ui_analysis = result

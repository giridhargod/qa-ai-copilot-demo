#agents/ui_agent.py
from agents.base_agent import BaseAgent
from agents.prompts import UI_AGENT_PROMPT
from models.workflow_state import WorkflowState


class UIAnalysisAgent(BaseAgent):

    def __init__(self, llm_service):
        self.llm_service = llm_service

    @property
    def name(self):
        return "UIAnalysisAgent"

    def execute(
        self,
        state: WorkflowState
    ) -> WorkflowState:

        prompt = f"""
{UI_AGENT_PROMPT}

Input:
{state.sanitized_input}
"""

        result = self.llm_service.generate(prompt)

        state.ui_analysis = result

        return state
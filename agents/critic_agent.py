#agents/critic_agent.py
from agents.base_agent import BaseAgent
from agents.prompts import CRITIC_AGENT_PROMPT
from models.workflow_state import WorkflowState


class CriticAgent(BaseAgent):

    def __init__(self, llm_service):
        self.llm_service = llm_service

    @property
    def name(self):
        return "CriticAgent"

    def execute(
        self,
        state: WorkflowState
    ) -> WorkflowState:

        prompt = f"""
{CRITIC_AGENT_PROMPT}

Testcases:
{state.testcases}
"""

        result = self.llm_service.generate(prompt)

        state.critic_review = result

        return state
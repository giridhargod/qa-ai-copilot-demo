#agents/critic_agent.py
from agents.base_agent import LLMAgent
from agents.prompts import CRITIC_AGENT_PROMPT
from models.workflow_state import WorkflowState


class CriticAgent(LLMAgent):

    prompt_template = CRITIC_AGENT_PROMPT
    input_label = "Testcases"

    @property
    def name(self):
        return "CriticAgent"

    def get_input(self, state: WorkflowState):
        return state.testcases

    def store_result(self, state: WorkflowState, result):
        state.critic_review = result

#agents/testcase_agent.py
from agents.base_agent import LLMAgent
from agents.prompts import TESTCASE_AGENT_PROMPT
from models.workflow_state import WorkflowState


class TestcaseGenerationAgent(LLMAgent):

    prompt_template = TESTCASE_AGENT_PROMPT

    @property
    def name(self):
        return "TestcaseGenerationAgent"

    def get_input(self, state: WorkflowState):
        return state.ui_analysis

    def store_result(self, state: WorkflowState, result):
        state.testcases = result.get(
            "testcases",
            []
        )

from agents.base_agent import BaseAgent
from agents.prompts import TESTCASE_AGENT_PROMPT
from models.workflow_state import WorkflowState


class TestcaseGenerationAgent(BaseAgent):

    def __init__(self, llm_service):
        self.llm_service = llm_service

    @property
    def name(self):
        return "TestcaseGenerationAgent"

    def execute(
        self,
        state: WorkflowState
    ) -> WorkflowState:

        prompt = f"""
{TESTCASE_AGENT_PROMPT}

Input:
{state.ui_analysis}
"""

        result = self.llm_service.generate(prompt)

        state.testcases = result.get(
            "testcases",
            []
        )

        return state
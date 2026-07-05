#agents/base_agent.py
from abc import ABC, abstractmethod


class BaseAgent(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def execute(self, state):
        pass


class LLMAgent(BaseAgent):
    """
    Shared execution wiring for agents that build a prompt from
    WorkflowState, call the LLM service once, and store the result
    back onto WorkflowState.

    Subclasses only need to define:
    - name            (from BaseAgent)
    - prompt_template
    - get_input(state)
    - store_result(state, result)

    input_label may be overridden when a subclass's prompt uses a
    label other than "Input" (e.g. "Testcases").
    """

    prompt_template = ""
    input_label = "Input"

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def get_input(self, state):
        raise NotImplementedError

    def store_result(self, state, result):
        raise NotImplementedError

    def execute(self, state):

        prompt = f"""
{self.prompt_template}

{self.input_label}:
{self.get_input(state)}
"""

        result = self.llm_service.generate(prompt)

        self.store_result(state, result)

        return state
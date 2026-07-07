#agents/base_agent.py
from abc import ABC, abstractmethod

from governance.output_validator import (
    OutputValidationError,
    is_non_empty_mapping,
)


class BaseAgent(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def execute(self, state):
        pass

    def gate_check(self, state):
        """
        Optional hook: a Skill/Critic may return a GateDecision here
        to tell the Governance runtime whether the workflow should
        proceed past this step. Returning None (the default) means
        this step has no opinion — Governance always proceeds.

        This is the only channel Governance uses to learn about
        domain-specific verdicts; it never inspects WorkflowState's
        business fields (confidence, approved, needs_sme, ...)
        directly. Agents that need to gate should translate their own
        Critic's verdict into a GateDecision here.
        """
        return None


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

    def validate_result(self, result) -> bool:
        """
        Minimal domain-neutral contract: the LLM must have returned
        a non-empty dict. Subclasses whose output has known required
        keys (e.g. a critic needing "approved"/"confidence") should
        override this with a stricter check — that stricter check is
        domain knowledge and belongs with the agent, not Governance.
        """
        return is_non_empty_mapping(result)

    def execute(self, state):

        prompt = f"""
{self.prompt_template}

{self.input_label}:
{self.get_input(state)}
"""

        result = self.llm_service.generate(prompt)

        if not self.validate_result(result):
            raise OutputValidationError(
                f"{self.name} produced output that failed validation: "
                f"{result!r}"
            )

        self.store_result(state, result)

        return state
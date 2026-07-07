#tests/test_output_validation.py
import pytest

from agents.base_agent import LLMAgent
from governance.output_validator import (
    OutputValidationError,
    is_non_empty_mapping,
)
from governance.execution_guard import ExecutionGuard
from governance.retry_policy import RetryPolicy


def test_is_non_empty_mapping_rejects_empty_dict():
    assert is_non_empty_mapping({}) is False


def test_is_non_empty_mapping_rejects_non_dict():
    assert is_non_empty_mapping(None) is False
    assert is_non_empty_mapping("oops") is False
    assert is_non_empty_mapping([]) is False


def test_is_non_empty_mapping_accepts_populated_dict():
    assert is_non_empty_mapping({"key": "value"}) is True


class _FakeLLMService:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1
        return self.result


class _StubLLMAgent(LLMAgent):
    prompt_template = "does not matter"

    @property
    def name(self):
        return "StubLLMAgent"

    def get_input(self, state):
        return "input"

    def store_result(self, state, result):
        state["result"] = result


def test_llm_agent_raises_on_empty_result():
    agent = _StubLLMAgent(_FakeLLMService({}))

    with pytest.raises(OutputValidationError):
        agent.execute({})


def test_llm_agent_stores_result_when_valid():
    agent = _StubLLMAgent(_FakeLLMService({"ok": True}))

    state = agent.execute({})

    assert state["result"] == {"ok": True}


def test_execution_guard_maps_validation_error_to_failed_validation_without_retry():
    llm_service = _FakeLLMService({})
    agent = _StubLLMAgent(llm_service)
    guard = ExecutionGuard(
        retry_policy=RetryPolicy(max_attempts=3, transient_exceptions=(Exception,))
    )

    outcome = guard.run(agent, {})

    assert outcome.succeeded is False
    assert outcome.record.status == "FAILED_VALIDATION"
    assert llm_service.calls == 1  # never retried, even though RetryPolicy would allow it

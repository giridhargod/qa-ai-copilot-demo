#tests/test_gate_engine.py
from governance.gate_engine import GateEngine
from governance.contracts import GateDecision
from governance.status import WorkflowStatus


class _SilentAgent:
    """An agent that never overrides gate_check — mirrors the
    BaseAgent default of "no opinion"."""
    name = "SilentAgent"

    def gate_check(self, state):
        return None


class _BlockingAgent:
    name = "BlockingAgent"

    def gate_check(self, state):
        return GateDecision(
            proceed=False,
            status=WorkflowStatus.PAUSED_FOR_REVIEW,
            reason="test block",
        )


def test_agent_with_no_opinion_always_proceeds():
    engine = GateEngine()
    decision = engine.evaluate(_SilentAgent(), state=None)

    assert decision.proceed is True
    assert decision.status == WorkflowStatus.RUNNING


def test_agent_decision_is_passed_through_unchanged():
    engine = GateEngine()
    decision = engine.evaluate(_BlockingAgent(), state=None)

    assert decision.proceed is False
    assert decision.status == WorkflowStatus.PAUSED_FOR_REVIEW
    assert decision.reason == "test block"

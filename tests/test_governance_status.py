#tests/test_governance_status.py
import pytest

from governance import WorkflowStatus, GateDecision
from models import WorkflowState


def test_workflow_state_defaults_to_not_started():
    state = WorkflowState()
    assert state.status == WorkflowStatus.NOT_STARTED
    assert state.status_reason == ""


def test_running_is_not_terminal():
    assert WorkflowStatus.RUNNING.is_terminal is False
    assert WorkflowStatus.NOT_STARTED.is_terminal is False


@pytest.mark.parametrize(
    "status",
    [
        WorkflowStatus.PAUSED_FOR_REVIEW,
        WorkflowStatus.NEEDS_SME,
        WorkflowStatus.FAILED_VALIDATION,
        WorkflowStatus.FAILED_AGENT,
        WorkflowStatus.COMPLETED,
    ],
)
def test_all_non_running_statuses_are_terminal(status):
    assert status.is_terminal is True


@pytest.mark.parametrize(
    "status",
    [
        WorkflowStatus.PAUSED_FOR_REVIEW,
        WorkflowStatus.NEEDS_SME,
        WorkflowStatus.FAILED_VALIDATION,
        WorkflowStatus.FAILED_AGENT,
    ],
)
def test_halting_statuses_are_not_completed(status):
    assert status.is_halt is True


def test_completed_is_terminal_but_not_a_halt():
    assert WorkflowStatus.COMPLETED.is_terminal is True
    assert WorkflowStatus.COMPLETED.is_halt is False


def test_gate_decision_allows_proceed_with_any_status():
    decision = GateDecision(proceed=True, status=WorkflowStatus.RUNNING)
    assert decision.proceed is True


def test_gate_decision_rejects_non_halt_status_when_not_proceeding():
    with pytest.raises(ValueError):
        GateDecision(proceed=False, status=WorkflowStatus.RUNNING)


def test_gate_decision_accepts_halt_status_when_not_proceeding():
    decision = GateDecision(
        proceed=False,
        status=WorkflowStatus.NEEDS_SME,
        reason="SME review required",
    )
    assert decision.proceed is False
    assert decision.reason == "SME review required"

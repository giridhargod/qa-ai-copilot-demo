#tests/test_execution_guard.py
from governance.execution_guard import ExecutionGuard
from governance.retry_policy import RetryPolicy


class _FakeState:
    """Minimal stand-in for WorkflowState — the guard never inspects
    workflow-specific fields, only passes state through."""
    pass


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class _SucceedsImmediately:
    name = "SucceedsImmediately"

    def execute(self, state):
        return state


class _FailsThenSucceeds:
    name = "FailsThenSucceeds"

    def __init__(self):
        self.calls = 0

    def execute(self, state):
        self.calls += 1
        if self.calls == 1:
            raise TransientError("temporary hiccup")
        return state


class _AlwaysFailsTransiently:
    name = "AlwaysFailsTransiently"

    def __init__(self):
        self.calls = 0

    def execute(self, state):
        self.calls += 1
        raise TransientError("still down")


class _FailsPermanently:
    name = "FailsPermanently"

    def execute(self, state):
        raise PermanentError("bad request")


def test_successful_agent_produces_success_record():
    guard = ExecutionGuard()
    outcome = guard.run(_SucceedsImmediately(), _FakeState())

    assert outcome.succeeded is True
    assert outcome.record.status == "SUCCESS"
    assert outcome.record.error_message is None


def test_non_transient_failure_does_not_retry():
    agent = _FailsPermanently()
    guard = ExecutionGuard(
        retry_policy=RetryPolicy(max_attempts=3, transient_exceptions=(TransientError,))
    )

    outcome = guard.run(agent, _FakeState())

    assert outcome.succeeded is False
    assert outcome.record.status == "FAILED_AGENT"
    assert "bad request" in outcome.record.error_message


def test_transient_failure_is_retried_and_can_succeed():
    agent = _FailsThenSucceeds()
    guard = ExecutionGuard(
        retry_policy=RetryPolicy(max_attempts=2, transient_exceptions=(TransientError,))
    )

    outcome = guard.run(agent, _FakeState())

    assert outcome.succeeded is True
    assert agent.calls == 2


def test_transient_failure_exhausts_retry_budget():
    agent = _AlwaysFailsTransiently()
    guard = ExecutionGuard(
        retry_policy=RetryPolicy(max_attempts=2, transient_exceptions=(TransientError,))
    )

    outcome = guard.run(agent, _FakeState())

    assert outcome.succeeded is False
    assert outcome.record.status == "FAILED_AGENT"
    assert agent.calls == 2


def test_default_retry_policy_retries_nothing():
    agent = _FailsThenSucceeds()
    guard = ExecutionGuard()  # default RetryPolicy: max_attempts=1, no transient types

    outcome = guard.run(agent, _FakeState())

    assert outcome.succeeded is False
    assert agent.calls == 1

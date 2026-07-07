#governance/execution_guard.py
from dataclasses import dataclass
from typing import Optional

from governance.retry_policy import RetryPolicy
from governance.output_validator import OutputValidationError
from models.execution_record import ExecutionRecord
from services.time_service import TimeService


@dataclass
class ExecutionOutcome:
    """Result of running one agent step through the ExecutionGuard."""

    state: object
    record: ExecutionRecord
    succeeded: bool


class ExecutionGuard:
    """
    Runs a single agent step safely: catches exceptions and applies
    the configured RetryPolicy, producing an honest ExecutionRecord
    either way.

    Deliberately narrow scope: this class does not know about
    WorkflowStatus, gating, or whether a failed step should halt the
    whole run — that is the orchestrator's job (via WorkflowStep and
    the Gate Engine), driven by whether the step is critical. The
    guard's only responsibility is "did this step run, and if not,
    why" — single responsibility, independently testable without any
    workflow-level concepts in scope.
    """

    def __init__(self, retry_policy: Optional[RetryPolicy] = None):
        self.retry_policy = retry_policy or RetryPolicy()

    def run(self, agent, state) -> ExecutionOutcome:

        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < self.retry_policy.max_attempts:
            attempts += 1

            try:
                state = agent.execute(state)

                return ExecutionOutcome(
                    state=state,
                    record=ExecutionRecord(
                        agent_name=agent.name,
                        status="SUCCESS",
                        executed_at=TimeService.get_current_ist(),
                    ),
                    succeeded=True,
                )

            except OutputValidationError as exc:
                # A contract violation, not an infrastructure failure —
                # never transient, so it is never worth retrying.
                return ExecutionOutcome(
                    state=state,
                    record=ExecutionRecord(
                        agent_name=agent.name,
                        status="FAILED_VALIDATION",
                        executed_at=TimeService.get_current_ist(),
                        error_message=str(exc),
                    ),
                    succeeded=False,
                )

            except Exception as exc:
                last_error = exc

                if not self.retry_policy.is_transient(exc):
                    break

        return ExecutionOutcome(
            state=state,
            record=ExecutionRecord(
                agent_name=agent.name,
                status="FAILED_AGENT",
                executed_at=TimeService.get_current_ist(),
                error_message=str(last_error),
            ),
            succeeded=False,
        )

#governance/contracts.py
from dataclasses import dataclass

from governance.status import WorkflowStatus


@dataclass(frozen=True)
class GateDecision:
    """
    The one contract Skills/Critics use to talk to the Governance
    runtime. A Skill or Critic decides what its own output means;
    Governance only ever reads this shape, never the domain fields
    (confidence, approved, needs_sme, ...) that produced it.

    proceed=True means the workflow may continue to the next step.
    proceed=False means Governance halts the run and records `status`
    (which must be a halting status) and `reason` on WorkflowState.
    """

    proceed: bool
    status: WorkflowStatus
    reason: str = ""

    def __post_init__(self):
        if not self.proceed and not self.status.is_halt:
            raise ValueError(
                f"GateDecision(proceed=False) requires a halting "
                f"WorkflowStatus, got {self.status!r}"
            )

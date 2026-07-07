#governance/status.py
from enum import Enum


class WorkflowStatus(Enum):
    """
    Enterprise workflow run status.

    This vocabulary belongs to the Governance runtime, not to any Skill
    or Critic. A Skill/Critic decides *what happened* (e.g. "confidence
    too low"); Governance only records *which of these fixed states*
    that decision maps to.
    """

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    PAUSED_FOR_REVIEW = "PAUSED_FOR_REVIEW"
    NEEDS_SME = "NEEDS_SME"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    FAILED_AGENT = "FAILED_AGENT"
    COMPLETED = "COMPLETED"

    @property
    def is_terminal(self) -> bool:
        return self != WorkflowStatus.RUNNING and self != WorkflowStatus.NOT_STARTED

    @property
    def is_halt(self) -> bool:
        """True for any terminal status that stops the pipeline before COMPLETED."""
        return self.is_terminal and self != WorkflowStatus.COMPLETED

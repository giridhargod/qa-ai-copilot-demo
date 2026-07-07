#governance/workflow_step.py
from dataclasses import dataclass


@dataclass
class WorkflowStep:
    """
    Declarative binding of one agent into the orchestrator's step
    list — the extension point future Skills use without touching
    the orchestrator's loop.

    `critical` controls graceful degradation: a failure in a
    non-critical step is logged but does not halt the run. Gating is
    deliberately not a separate field here — any agent may implement
    BaseAgent.gate_check() to participate in governance; the
    orchestrator always asks after a successful execution via
    GateEngine, and an agent with nothing to say simply returns None.
    """

    agent: object
    critical: bool = True

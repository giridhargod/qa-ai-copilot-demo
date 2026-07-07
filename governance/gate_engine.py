#governance/gate_engine.py
from governance.contracts import GateDecision
from governance.status import WorkflowStatus


class GateEngine:
    """
    Mechanically enforces whatever GateDecision a step's agent
    produces. Contains zero domain knowledge: it never reads
    "confidence", "approved", "needs_sme", or any other business
    field — it only knows the neutral GateDecision contract.

    Skills/Critics decide; GateEngine only executes that decision by
    asking BaseAgent.gate_check(state) and defaulting to "proceed"
    when a step has no opinion.
    """

    _PROCEED = GateDecision(proceed=True, status=WorkflowStatus.RUNNING)

    def evaluate(self, agent, state) -> GateDecision:
        decision = agent.gate_check(state)
        return decision if decision is not None else self._PROCEED

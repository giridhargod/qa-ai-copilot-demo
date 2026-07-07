#tests/test_requirement_readiness_gate.py
from critics.requirement_readiness_critic import (
    RequirementReadinessCritic,
    HARD_FAIL_CONFIDENCE,
)
from governance.status import WorkflowStatus


def test_approved_verdict_proceeds():
    decision = RequirementReadinessCritic.to_gate_decision(
        {"approved": True, "confidence": 95, "needs_sme": False}
    )
    assert decision.proceed is True
    assert decision.status == WorkflowStatus.RUNNING


def test_needs_sme_halts_regardless_of_approval():
    decision = RequirementReadinessCritic.to_gate_decision(
        {"approved": True, "confidence": 95, "needs_sme": True}
    )
    assert decision.proceed is False
    assert decision.status == WorkflowStatus.NEEDS_SME


def test_low_confidence_below_hard_floor_fails_validation():
    decision = RequirementReadinessCritic.to_gate_decision(
        {
            "approved": False,
            "confidence": HARD_FAIL_CONFIDENCE - 1,
            "needs_sme": False,
        }
    )
    assert decision.proceed is False
    assert decision.status == WorkflowStatus.FAILED_VALIDATION


def test_borderline_confidence_pauses_for_review():
    decision = RequirementReadinessCritic.to_gate_decision(
        {
            "approved": False,
            "confidence": HARD_FAIL_CONFIDENCE + 10,
            "needs_sme": False,
        }
    )
    assert decision.proceed is False
    assert decision.status == WorkflowStatus.PAUSED_FOR_REVIEW


def test_missing_fields_default_safely_to_a_halt():
    # An empty/malformed verdict should never silently proceed.
    decision = RequirementReadinessCritic.to_gate_decision({})
    assert decision.proceed is False

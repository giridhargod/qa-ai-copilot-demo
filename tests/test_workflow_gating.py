#tests/test_workflow_gating.py
from unittest.mock import patch

from governance.status import WorkflowStatus
from governance.workflow_step import WorkflowStep
from workflows.workflow import WorkflowOrchestrator


def _readiness_result(approved, confidence, needs_sme=False):
    return {
        "requirements": [],
        "quality": {"status": "READY" if approved else "NOT_READY"},
        "review": {"status": "READY" if approved else "NOT_READY"},
        "critic": {
            "approved": approved,
            "confidence": confidence,
            "needs_sme": needs_sme,
            "warnings": [],
            "recommendations": [],
            "reasoning": [],
        },
    }


def _isolated_orchestrator():
    """An orchestrator whose only step is Requirement Readiness, so
    the test never has to reach (or mock) the downstream LLM agents
    just to exercise the gate."""
    orchestrator = WorkflowOrchestrator()
    orchestrator.steps = [
        WorkflowStep(orchestrator.requirement_readiness_agent)
    ]
    return orchestrator


@patch("services.readiness_service.ReadinessService.analyze")
def test_approved_requirement_proceeds_to_completion(mock_analyze):
    mock_analyze.return_value = _readiness_result(approved=True, confidence=95)

    state = _isolated_orchestrator().run("well-formed requirement text")

    assert state.status == WorkflowStatus.COMPLETED
    assert len(state.execution_log) == 2  # PII + readiness only


@patch("services.readiness_service.ReadinessService.analyze")
def test_needs_sme_halts_before_any_ai_step(mock_analyze):
    mock_analyze.return_value = _readiness_result(
        approved=True, confidence=95, needs_sme=True
    )

    state = _isolated_orchestrator().run("ambiguous requirement text")

    assert state.status == WorkflowStatus.NEEDS_SME
    assert state.status_reason
    assert state.ui_analysis == {}  # never reached UIAnalysisAgent


@patch("services.readiness_service.ReadinessService.analyze")
def test_low_confidence_fails_validation(mock_analyze):
    mock_analyze.return_value = _readiness_result(approved=False, confidence=10)

    state = _isolated_orchestrator().run("garbage input")

    assert state.status == WorkflowStatus.FAILED_VALIDATION
    assert state.ui_analysis == {}


@patch("services.readiness_service.ReadinessService.analyze")
def test_borderline_confidence_pauses_for_review(mock_analyze):
    mock_analyze.return_value = _readiness_result(approved=False, confidence=60)

    state = _isolated_orchestrator().run("borderline requirement text")

    assert state.status == WorkflowStatus.PAUSED_FOR_REVIEW
    assert state.ui_analysis == {}

# models/workflow_state.py
from dataclasses import dataclass, field
from models.execution_record import ExecutionRecord


@dataclass
class WorkflowState:

    raw_input: str = ""

    sanitized_input: str = ""

    pii_report: dict = field(default_factory=dict)

    requirements: list = field(default_factory=list)

    requirement_quality: dict = field(
        default_factory=dict
    )

    requirement_review: dict = field(
        default_factory=dict
    )

    ui_analysis: dict = field(
        default_factory=dict
    )

    impact_analysis: dict = field(
        default_factory=dict
    )

    testcases: list = field(
        default_factory=list
    )

    critic_reviews: dict = field(
        default_factory=dict
    )

    traceability_matrix: list = field(
        default_factory=list
    )

    coverage_metrics: dict = field(
        default_factory=dict
    )

    execution_log: list[ExecutionRecord] = field(
        default_factory=list
    )

    workflow_metrics: dict = field(
    default_factory=dict
    )

    evaluation_metrics: dict = field(
    default_factory=dict
    )
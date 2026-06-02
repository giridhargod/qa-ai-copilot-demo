from dataclasses import dataclass, field


@dataclass
class WorkflowState:

    raw_input: str = ""

    sanitized_input: str = ""

    pii_report: dict = field(default_factory=dict)

    ui_analysis: dict = field(default_factory=dict)

    impact_analysis: dict = field(default_factory=dict)

    testcases: list = field(default_factory=list)

    critic_review: dict = field(default_factory=dict)

    execution_log: list = field(default_factory=list)
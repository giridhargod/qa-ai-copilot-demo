#workflows/workflow.py
from agents.requirement_readiness_agent import (
    RequirementReadinessAgent
)
from datetime import datetime
from agents import (
    UIAnalysisAgent,
    ImpactAnalysisAgent,
    TestcaseGenerationAgent,
    CriticAgent
)

from models import WorkflowState
from services import OpenAIService
from services.openai_service import TRANSIENT_EXCEPTIONS
from services.pii_service import process_pii
from models import ExecutionRecord
from services import TimeService
from governance import WorkflowStatus
from governance.execution_guard import ExecutionGuard
from governance.retry_policy import RetryPolicy
from governance.gate_engine import GateEngine
from governance.workflow_step import WorkflowStep

class WorkflowOrchestrator:

    def __init__(self):

        llm_service = OpenAIService()

        self.execution_guard = ExecutionGuard(
            retry_policy=RetryPolicy(
                max_attempts=2,
                transient_exceptions=TRANSIENT_EXCEPTIONS,
            )
        )

        self.gate_engine = GateEngine()

        self.requirement_readiness_agent = (
            RequirementReadinessAgent()
        )

        self.steps = [

            WorkflowStep(self.requirement_readiness_agent),

            WorkflowStep(UIAnalysisAgent(
                llm_service
            )),

            WorkflowStep(ImpactAnalysisAgent(
                llm_service
            )),

            WorkflowStep(TestcaseGenerationAgent(
                llm_service
            )),

            WorkflowStep(CriticAgent(
                llm_service
            ))
        ]

    def run(
        self,
        user_input: str
    ) -> WorkflowState:

        state = WorkflowState()

        state.status = WorkflowStatus.RUNNING

        workflow_start = datetime.now()

        state.raw_input = user_input

        pii_result = process_pii(user_input)

        state.pii_report = pii_result

        state.sanitized_input = pii_result.get(
            "sanitized",
            user_input
        )

        state.execution_log.append(
            ExecutionRecord(
                agent_name="PII Processor",
                status="SUCCESS",
                executed_at=TimeService.get_current_ist()
            )
        )

        for step in self.steps:

            outcome = self.execution_guard.run(step.agent, state)

            state = outcome.state

            state.execution_log.append(outcome.record)

            if not outcome.succeeded:

                if not step.critical:
                    continue

                state.status = (
                    WorkflowStatus.FAILED_VALIDATION
                    if outcome.record.status == "FAILED_VALIDATION"
                    else WorkflowStatus.FAILED_AGENT
                )

                state.status_reason = (
                    f"{step.agent.name} failed: "
                    f"{outcome.record.error_message}"
                )

                return state

            decision = self.gate_engine.evaluate(step.agent, state)

            if not decision.proceed:

                state.status = decision.status

                state.status_reason = decision.reason

                return state

        from services.traceability_service import (
            TraceabilityService
        )
        from services.coverage_service import (
            CoverageService
        )

        state.traceability_matrix = (
            TraceabilityService.build_traceability(
                state.requirements,
                state.testcases
            )
        )

        state.coverage_metrics = (
            CoverageService.calculate(
                state.requirements,
                state.traceability_matrix
            )
        )

        from evaluation.testcase_quality_evaluator import (
            TestcaseQualityEvaluator
        )

        state.evaluation_metrics = (
            TestcaseQualityEvaluator.evaluate(
                state.testcases
            )
        )

        workflow_end = datetime.now()

        from services.metrics_service import (
            MetricsService
        )

        state.workflow_metrics = (
            MetricsService.build_metrics(
                workflow_start,
                workflow_end,
                state.requirements,
                state.testcases,
                state.execution_log
            )
        )

        state.status = WorkflowStatus.COMPLETED

        return state
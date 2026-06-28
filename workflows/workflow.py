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
from services.pii_service import process_pii
from models import ExecutionRecord
from services import TimeService

class WorkflowOrchestrator:

    def __init__(self):

        llm_service = OpenAIService()

        self.requirement_readiness_agent = (
            RequirementReadinessAgent()
        )

        self.agents = [

            self.requirement_readiness_agent,

            UIAnalysisAgent(
                llm_service
            ),

            ImpactAnalysisAgent(
                llm_service
            ),

            TestcaseGenerationAgent(
                llm_service
            ),

            CriticAgent(
                llm_service
            )
        ]

    def run(
        self,
        user_input: str
    ) -> WorkflowState:

        state = WorkflowState()

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

        for agent in self.agents:

            state = agent.execute(state)

            state.execution_log.append(
                ExecutionRecord(
                    agent_name=agent.name,
                    status="SUCCESS",
                    executed_at=TimeService.get_current_ist()
                )
            )

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

        return state
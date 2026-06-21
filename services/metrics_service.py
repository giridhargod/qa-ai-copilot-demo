#services/metrics_service.py
from datetime import datetime


class MetricsService:

    @staticmethod
    def build_metrics(
        start_time,
        end_time,
        requirements,
        testcases,
        execution_log
    ):

        duration = round(
            (end_time - start_time).total_seconds(),
            2
        )

        return {
            "workflow_duration_seconds": duration,
            "requirements_count": len(
                requirements
            ),
            "testcases_count": len(
                testcases
            ),
            "agents_executed": len(
                execution_log
            )
        }
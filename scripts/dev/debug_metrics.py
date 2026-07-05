#scripts/dev/debug_metrics.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from workflows.workflow import WorkflowOrchestrator

workflow = WorkflowOrchestrator()

result = workflow.run(
    """
    User can login using email and password

    User can reset password

    User can logout
    """
)

print()

print("WORKFLOW METRICS")

print(result.workflow_metrics)
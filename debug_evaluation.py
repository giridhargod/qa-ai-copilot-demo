#debug_evaluation.py
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
print("EVALUATION METRICS")
print()

for key, value in result.evaluation_metrics.items():
    print(f"{key}: {value}")
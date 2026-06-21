# debug_traceability.py
from workflows.workflow import WorkflowOrchestrator

workflow = WorkflowOrchestrator()

result = workflow.run(
    "User logs in using email and password"
)

print("\nTRACEABILITY MATRIX\n")

for item in result.traceability_matrix:
    print(item)
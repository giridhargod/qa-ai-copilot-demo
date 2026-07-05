# scripts/dev/debug_traceability.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from workflows.workflow import WorkflowOrchestrator

workflow = WorkflowOrchestrator()

result = workflow.run(
    "User logs in using email and password"
)

print("\nTRACEABILITY MATRIX\n")

for item in result.traceability_matrix:
    print(item)
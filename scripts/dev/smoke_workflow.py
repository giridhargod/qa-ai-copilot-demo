#scripts/dev/smoke_workflow.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from workflows.workflow import WorkflowOrchestrator

sample_requirement = """
Administrator shall login using Email and Password.

Password shall contain at least 8 characters.

System shall lock the account after 5 failed attempts.

Response time shall be below 3 seconds.

Application shall support keyboard navigation.
"""

workflow = WorkflowOrchestrator()

result = workflow.run(
    sample_requirement
)

print("=" * 80)
print("REQUIREMENT READINESS")
print("=" * 80)

print(result.requirement_quality)

print()

print(result.requirement_review)

print()

print("=" * 80)
print("CRITIC REVIEWS")
print("=" * 80)

print(result.critic_reviews)

assert len(result.critic_reviews) == 2, (
    f"expected 2 critic verdicts, got {list(result.critic_reviews)}"
)

print()

print("=" * 80)
print("REQUIREMENTS")
print("=" * 80)

for requirement in result.requirements:

    print(requirement)

print()

print("=" * 80)
print("TEST CASES")
print("=" * 80)

for testcase in result.testcases:

    print(testcase["title"])

print()

print("=" * 80)
print("WORKFLOW METRICS")
print("=" * 80)

print(result.workflow_metrics)
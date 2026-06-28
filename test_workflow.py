#test_workflow.py
from workflows.workflow import WorkflowOrchestrator

sample_requirement = """
Administrator shall login using Email and Password.

Password shall contain at least 8 characters.

System shall lock the account after 5 failed attempts.

Response time shall be below 3 seconds.

Application shall support keyboard navigation.
"""

workflow = WorkflowOrchestrator()

result = workflow.run(sample_requirement)

print("=" * 80)
print("REQUIREMENT READINESS")
print("=" * 80)

print(result.requirement_quality)

print()

print(result.requirement_review)

print()

print("=" * 80)
print("REQUIREMENTS")
print("=" * 80)

for req in result.requirements:
    print(req)

print()

print("=" * 80)
print("TESTCASES")
print("=" * 80)

for tc in result.testcases:
    print(tc["title"])

print()

print("=" * 80)
print("WORKFLOW METRICS")
print("=" * 80)

print(result.workflow_metrics)
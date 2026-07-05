#scripts/dev/smoke_requirement_engine.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.readiness_service import ReadinessService

sample_requirement = """
Administrator shall login.

Password is mandatory.

Session shall timeout after 15 minutes.

Response shall be within 3 seconds.

Application shall support keyboard navigation.
"""

result = ReadinessService.analyze(
    sample_requirement
)

print("=" * 80)
print("REQUIREMENT ENGINE OUTPUT")
print("=" * 80)

for requirement in result["requirements"]:

    print(requirement)

    print("-" * 80)

print()

print("=" * 80)
print("QUALITY REPORT")
print("=" * 80)

print(result["quality"])

print()

print("=" * 80)
print("READINESS REVIEW")
print("=" * 80)

print(result["review"])

print()

print("=" * 80)
print("CRITIC REPORT")
print("=" * 80)

print(result["critic"])
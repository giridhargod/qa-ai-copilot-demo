from requirement_engine.extractor import RequirementExtractor
from requirement_engine.classifier import RequirementClassifier
from requirement_engine.validator import RequirementValidator
from requirement_engine.quality import RequirementQualityScorer
from requirement_engine.reviewer import RequirementReviewer

text = """
Administrator shall login.

Password is mandatory.

Session shall timeout after 15 minutes.

Response shall be within 3 seconds.

Application shall support keyboard navigation.
"""

# -----------------------------
# Step 1 - Extract
# -----------------------------
requirements = RequirementExtractor.extract(text)

# -----------------------------
# Step 2 - Classify
# -----------------------------
requirements = [
    RequirementClassifier.classify(req)
    for req in requirements
]

# -----------------------------
# Step 3 - Validate
# -----------------------------
requirements = RequirementValidator.validate(requirements)

quality_report = RequirementQualityScorer.evaluate(
    requirements
)

requirements = RequirementReviewer.review(
    requirements
)

# -----------------------------
# Step 4 - Display Results
# -----------------------------
print("\n===== REQUIREMENT ENGINE OUTPUT =====\n")

for req in requirements:
    print(req)
    print("-" * 80)

print("\n")
print("=" * 80)
print(" REQUIREMENT READINESS REPORT ")
print("=" * 80)

for key, value in quality_report.items():
    print(f"{key}: {value}")

print("\n")
print("=" * 80)
print(" REQUIREMENT REVIEW ")
print("=" * 80)
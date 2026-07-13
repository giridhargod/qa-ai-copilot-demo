"""Data contracts for the Secure Test Step Generator pipeline.

Kept in one flat module deliberately -- these are small dataclasses
and splitting them into one-file-per-class would be unnecessary
ceremony for a package this size.

The type boundary between EvidenceItem and SanitizedEvidenceItem is
the security boundary, not just naming: EvidenceItem carries raw
image bytes and raw (unsanitized) text straight out of the source
document. SanitizedEvidenceItem carries only sanitized text. Every
function that talks to the LLM (step_generator.py) accepts
SanitizedEvidenceItem, never EvidenceItem -- so a reviewer can
confirm the "no raw screenshots/PII reach the LLM" rule by checking
type signatures, not by re-reading every line of prompt-building code.
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CursorHint:
    """Best-effort, local-only signal about where the SnagIt cursor
    preview appears in a screenshot. Approximate by nature -- see
    ocr.py's docstring for the heuristic's known limitations.
    """

    description: str
    confidence: float


@dataclass
class EvidenceItem:
    """One screenshot + its surrounding context, in document order.
    Raw: image bytes and notes text here have NOT been sanitized yet.
    Nothing in this type may be passed to step_generator.py / an LLM.
    """

    order: int
    image_bytes: bytes
    notes_text: str = ""
    source_ref: str = ""  # e.g. "page 3" or "paragraph 12", for traceability in warnings

    # Populated by ocr.py, still raw/unsanitized.
    ocr_text: str = ""
    cursor_hint: "CursorHint | None" = None


@dataclass
class SanitizationReport:
    """Per-category redaction counts. Category names come from
    patterns.py so this stays in sync automatically.
    """

    counts_by_category: dict = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.counts_by_category.values())

    def merge(self, other: "SanitizationReport") -> "SanitizationReport":
        merged = dict(self.counts_by_category)
        for category, count in other.counts_by_category.items():
            merged[category] = merged.get(category, 0) + count
        return SanitizationReport(counts_by_category=merged)


@dataclass
class SanitizedEvidenceItem:
    """The only evidence shape step_generator.py is allowed to see."""

    order: int
    sanitized_notes: str
    sanitized_ocr_text: str
    cursor_hint: "CursorHint | None"
    source_ref: str = ""


@dataclass
class TestStep:
    """One row of the generated Excel output."""

    # Tells pytest this is a data class, not a test class to collect
    # (name collision with pytest's own "Test*" discovery convention).
    __test__ = False

    step_no: int
    action: str
    expected_result: str
    confidence: float  # 0.0 - 1.0
    confidence_reason: str = ""
    warnings: list = field(default_factory=list)

    # Future-review readiness only (per Architect decision #5) -- no
    # workflow reads or acts on this in V1, it just leaves room for
    # QA AI Copilot's future human-review layer to plug in later
    # without a schema change.
    status: str = "GENERATED"


@dataclass
class GenerationResult:
    """Final output of a full pipeline run."""

    source_document: str
    steps: list = field(default_factory=list)  # list[TestStep]
    sanitization_summary: SanitizationReport = field(
        default_factory=SanitizationReport
    )
    run_warnings: list = field(default_factory=list)  # e.g. "page 4 OCR failed"
    generated_at: datetime = field(default_factory=datetime.now)

    # Set by pipeline.py after excel_exporter.export_to_excel() runs --
    # unknown at construction time since the filename is derived from
    # source_document inside the exporter itself.
    output_path: str = ""

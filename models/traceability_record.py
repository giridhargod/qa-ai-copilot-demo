#models/traceability_record.py
from dataclasses import dataclass, field

@dataclass
class TraceabilityRecord:

    requirement_id: str

    requirement_text: str

    testcase_ids: list[str] = field(
        default_factory=list
    )
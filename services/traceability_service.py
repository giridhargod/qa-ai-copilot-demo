#services/traceability_service.py
from models.traceability_record import TraceabilityRecord

class TraceabilityService:

    @staticmethod
    def build_traceability(
        requirements,
        testcases
    ):

        records = []

        testcase_ids = [
            tc.get("id", "UNKNOWN")
            for tc in testcases
        ]

        for requirement in requirements:

            records.append(
                TraceabilityRecord(
                    requirement_id=requirement["id"],
                    requirement_text=requirement["text"],
                    testcase_ids=testcase_ids
                )
            )

        return records
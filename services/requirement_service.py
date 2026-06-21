#services/requirement_service.py
from dataclasses import dataclass

@dataclass
class Requirement:

    id: str
    text: str

import re

class RequirementService:

    @staticmethod
    def extract_requirements(user_input):

        lines = [
            line.strip()
            for line in user_input.split("\n")
            if line.strip()
        ]

        requirements = []

        for index, line in enumerate(lines, start=1):

            cleaned = re.sub(
                r"^\d+[\.\)]\s*",
                "",
                line
            )

            requirements.append(
                {
                    "id": f"REQ-{index:03d}",
                    "text": cleaned
                }
            )

        return requirements
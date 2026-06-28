#requirement_engine/extractor.py
"""
Requirement Extractor

Purpose
-------
Extract structured requirements from raw requirement text.

This module performs deterministic parsing only.
No AI reasoning should occur here.

Future enhancements:
- DOCX heading detection
- PDF section detection
- JIRA story parsing
- Azure DevOps work item parsing
"""

from typing import List, Dict
import re


class RequirementExtractor:
    """
    Extracts individual requirement statements from
    raw requirement text.
    """

    REQUIREMENT_PREFIX = "REQ"

    @classmethod
    def extract(
        cls,
        text: str
    ) -> List[Dict]:

        if not text or not text.strip():
            return []

        requirements = []

        current_id = 1

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Ignore headings made only of punctuation
            if re.fullmatch(r"[-_=]{3,}", line):
                continue

            requirements.append(
                {
                    "id": f"{cls.REQUIREMENT_PREFIX}-{current_id:03}",
                    "text": line,
                    "source": "document",
                    "status": "identified"
                }
            )

            current_id += 1

        return requirements
#schemas.py
from pydantic import BaseModel
from typing import List


class TestCase(BaseModel):
    id: int
    scenario: str
    steps: str
    expected: str


class FinalOutput(BaseModel):
    ui_analysis: str
    testcases: List[TestCase]
    critic: str
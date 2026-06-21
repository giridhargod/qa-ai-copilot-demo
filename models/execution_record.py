#models/execution_record.py
from dataclasses import dataclass

@dataclass
class ExecutionRecord:

    agent_name: str

    status: str

    executed_at: str
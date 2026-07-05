#scripts/dev/temp_test.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from services.openai_service import OpenAIService

service = OpenAIService()

print(type(service))
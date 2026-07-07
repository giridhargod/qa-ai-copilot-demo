#services/openai_service.py
import json

from openai import OpenAI
from openai import (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

from config.settings import OPENAI_API_KEY, OPENAI_MODEL

# Exception types considered transient (worth retrying) for this
# provider. Kept here, not in governance/, so Governance stays
# LLM-provider-agnostic per the platform's stable architecture
# decisions.
TRANSIENT_EXCEPTIONS = (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)


class OpenAIService:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        self.model = OPENAI_MODEL

    def generate(self, prompt):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        return self.extract_json(content)

    def extract_json(self, text):

        try:
            return json.loads(text)

        except:

            try:
                start = text.index("{")
                end = text.rindex("}") + 1

                return json.loads(
                    text[start:end]
                )

            except:

                return {}
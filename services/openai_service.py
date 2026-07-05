#services/openai_service.py
import json

from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL


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
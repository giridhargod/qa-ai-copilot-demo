import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class OpenAIService:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = "gpt-4o-mini"

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
"""AI Step Generation stage's LLM boundary.

LLMProvider is the only interface step_generator.py talks to, so the
package stays LLM-agnostic (a different provider can be dropped in
without touching step_generator.py). OpenAILLMProvider is the
concrete default. Deliberately not importing
qa-ai-copilot/services/openai_service.py -- this package stays
self-contained per Architect decision #1, at the cost of a small,
acceptable amount of duplication with that module.
"""
import json
from typing import Protocol

from openai import OpenAI, OpenAIError

from . import config


class LLMGenerationError(Exception):
    """Raised when the LLM call itself fails (auth, rate limit, timeout,
    network) -- distinct from a malformed/unparseable response, which
    generate() is expected to absorb by returning {} rather than raising.
    Lets cli.py give a clean message instead of a raw SDK traceback.
    """


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> dict:
        """Send prompt to the model and return a parsed JSON dict.
        Implementations should return {} on any malformed/unparseable
        response rather than raising -- validator.py is responsible
        for deciding what to do with an empty result. A failure to
        reach/authenticate with the provider itself should raise
        LLMGenerationError so callers can distinguish the two.
        """
        ...


class OpenAILLMProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)
        self.model = model or config.OPENAI_MODEL

    def generate(self, prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.2,
            )
        except OpenAIError as exc:
            raise LLMGenerationError(
                f"OpenAI request failed: {exc}"
            ) from exc

        content = response.choices[0].message.content
        return self._extract_json(content)

    @staticmethod
    def _extract_json(text: str) -> dict:
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            return {}

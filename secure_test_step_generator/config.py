"""Runtime configuration for the Secure Test Step Generator.

Loaded from environment variables / a local .env file so the package
has no dependency on qa-ai-copilot's config/settings.py. Nothing here
is hardcoded per the "no hardcoded paths/prompts" engineering rule.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _float_env(name: str, default: str) -> float:
    """Same as float(os.getenv(name, default)), but with an actionable
    error message instead of a bare traceback if a user's .env has a
    typo'd, non-numeric value -- these are user-editable config knobs,
    not internal constants, so a malformed value is expected to happen.
    """
    raw = os.getenv(name, default)
    try:
        return float(raw)
    except ValueError:
        raise ValueError(
            f"Invalid value for {name}: {raw!r} is not a number. "
            f"Check your .env file or environment configuration."
        ) from None


# LLM provider settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("STSG_OPENAI_MODEL", "gpt-4o-mini")

# Confidence below this threshold gets a mandatory Notes/Warning explanation
# rather than being silently reported as a bare number.
LOW_CONFIDENCE_THRESHOLD = _float_env("STSG_LOW_CONFIDENCE_THRESHOLD", "0.6")

# Cursor-hint heuristic (ocr.py) will not report a hint below this score.
CURSOR_HINT_MIN_CONFIDENCE = _float_env("STSG_CURSOR_HINT_MIN_CONFIDENCE", "0.55")

# Excel export
DEFAULT_OUTPUT_FILENAME = os.getenv(
    "STSG_OUTPUT_FILENAME", "test_steps.xlsx"
)

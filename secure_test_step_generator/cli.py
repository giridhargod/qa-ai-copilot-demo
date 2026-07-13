"""CLI adapter -- the only adapter this package ships in V1.

Zero business logic: parses arguments, wires the default LLM provider,
calls pipeline.run(), and prints a summary. Run as:

    python -m secure_test_step_generator.cli --input <doc.docx|doc.pdf> --output <folder>
"""
import argparse
import sys

from . import config, pipeline
from .llm_provider import LLMGenerationError, OpenAILLMProvider


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="secure-test-step-generator",
        description=(
            "Generate enterprise test steps (Action/Expected Result/"
            "Confidence) from a Word or PDF document containing "
            "screenshots, sanitizing sensitive data before any AI call."
        ),
    )
    parser.add_argument(
        "--input", required=True, help="Path to the input .docx or .pdf document."
    )
    parser.add_argument(
        "--output", required=True, help="Folder where the .xlsx result is written."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if not config.OPENAI_API_KEY:
        print(
            "ERROR: OPENAI_API_KEY is not set. Create a .env file "
            "(see README.md) or export it before running.",
            file=sys.stderr,
        )
        return 1

    llm_provider = OpenAILLMProvider()

    try:
        result = pipeline.run(args.input, args.output, llm_provider)
    except FileNotFoundError:
        print(f"ERROR: input document not found: {args.input}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except LLMGenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: could not write output: {exc}", file=sys.stderr)
        return 1

    low_confidence_count = sum(
        1 for step in result.steps if step.confidence < config.LOW_CONFIDENCE_THRESHOLD
    )
    warning_count = sum(1 for step in result.steps if step.warnings)

    print(f"Wrote {len(result.steps)} step(s) to: {result.output_path}")
    print(f"Sensitive values redacted: {result.sanitization_summary.total}")
    print(f"Steps below confidence threshold ({config.LOW_CONFIDENCE_THRESHOLD}): {low_confidence_count}")
    print(f"Steps with warnings: {warning_count}")

    if result.run_warnings:
        print("\nRun warnings:")
        for warning in result.run_warnings:
            print(f"  - {warning}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

from .. import cli
from ..models import GenerationResult, SanitizationReport, TestStep


def test_missing_api_key_returns_error_without_running_pipeline(monkeypatch, capsys):
    monkeypatch.setattr(cli.config, "OPENAI_API_KEY", None)
    exit_code = cli.main(["--input", "doc.docx", "--output", "out"])
    assert exit_code == 1
    assert "OPENAI_API_KEY" in capsys.readouterr().err


def test_missing_input_file_reports_clean_error(monkeypatch, capsys):
    monkeypatch.setattr(cli.config, "OPENAI_API_KEY", "fake-key")
    monkeypatch.setattr(cli, "OpenAILLMProvider", lambda: object())

    def fake_run(input_path, output_dir, llm_provider):
        raise FileNotFoundError()

    monkeypatch.setattr(cli.pipeline, "run", fake_run)

    exit_code = cli.main(["--input", "missing.docx", "--output", "out"])
    assert exit_code == 1
    assert "not found" in capsys.readouterr().err


def test_llm_api_failure_reports_clean_error_not_a_crash(monkeypatch, capsys):
    monkeypatch.setattr(cli.config, "OPENAI_API_KEY", "fake-key")
    monkeypatch.setattr(cli, "OpenAILLMProvider", lambda: object())

    def fake_run(input_path, output_dir, llm_provider):
        raise cli.LLMGenerationError("OpenAI request failed: rate limit exceeded")

    monkeypatch.setattr(cli.pipeline, "run", fake_run)

    exit_code = cli.main(["--input", "doc.docx", "--output", "out"])
    assert exit_code == 1
    assert "rate limit" in capsys.readouterr().err


def test_output_write_failure_reports_clean_error_not_a_crash(monkeypatch, capsys):
    monkeypatch.setattr(cli.config, "OPENAI_API_KEY", "fake-key")
    monkeypatch.setattr(cli, "OpenAILLMProvider", lambda: object())

    def fake_run(input_path, output_dir, llm_provider):
        raise PermissionError("Access is denied")

    monkeypatch.setattr(cli.pipeline, "run", fake_run)

    exit_code = cli.main(["--input", "doc.docx", "--output", "out"])
    assert exit_code == 1
    assert "could not write output" in capsys.readouterr().err


def test_successful_run_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(cli.config, "OPENAI_API_KEY", "fake-key")
    monkeypatch.setattr(cli, "OpenAILLMProvider", lambda: object())

    fake_result = GenerationResult(
        source_document="doc.docx",
        steps=[
            TestStep(step_no=1, action="A", expected_result="B", confidence=0.9),
            TestStep(
                step_no=2, action="C", expected_result="D", confidence=0.1,
                warnings=["low confidence"],
            ),
        ],
        sanitization_summary=SanitizationReport(counts_by_category={"ssn": 2}),
        run_warnings=["page 3 OCR failed"],
        output_path="out/doc_test_steps.xlsx",
    )

    monkeypatch.setattr(
        cli.pipeline, "run",
        lambda input_path, output_dir, llm_provider: fake_result,
    )

    exit_code = cli.main(["--input", "doc.docx", "--output", "out"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Wrote 2 step(s)" in out
    assert "Sensitive values redacted: 2" in out
    assert "page 3 OCR failed" in out

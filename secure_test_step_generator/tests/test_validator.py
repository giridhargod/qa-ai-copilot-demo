from ..models import TestStep
from ..validator import validate_steps


def test_well_formed_high_confidence_step_passes_through_clean():
    # Deliberately avoids two-consecutive-Capitalized-Word phrases (e.g.
    # "Click Submit") -- those now trip the person_name heuristic by
    # design; see test_sanitizer.py's name-masking characterization test.
    step = TestStep(
        step_no=1,
        action="Click the submit button",
        expected_result="Confirmation page appears",
        confidence=0.9,
        confidence_reason="OCR quality high; cursor detected",
        warnings=[],
    )
    result = validate_steps([step])[0]
    assert result.warnings == []
    assert result.action == "Click the submit button"


def test_flags_empty_action_or_expected_result():
    step = TestStep(step_no=1, action="", expected_result="", confidence=0.9)
    result = validate_steps([step])[0]
    assert any("requires manual authoring" in w for w in result.warnings)


def test_flags_low_confidence_without_reason():
    step = TestStep(
        step_no=1, action="Click X", expected_result="Y happens", confidence=0.2
    )
    result = validate_steps([step])[0]
    assert any("review manually" in w for w in result.warnings)


def test_low_confidence_with_reason_is_not_flagged_for_missing_reason():
    step = TestStep(
        step_no=1,
        action="Click X",
        expected_result="Y happens",
        confidence=0.2,
        confidence_reason="OCR text was too blurry to read clearly",
    )
    result = validate_steps([step])[0]
    assert not any("review manually" in w for w in result.warnings)


def test_redacts_leaked_sensitive_data_in_generated_text():
    step = TestStep(
        step_no=1,
        action="Verify claimant SSN 123-45-6789 matches record",
        expected_result="Record loads for the claimant",
        confidence=0.9,
        confidence_reason="",
    )
    result = validate_steps([step])[0]
    assert "123-45-6789" not in result.action
    assert "<SSN>" in result.action
    assert any("redacted" in w for w in result.warnings)

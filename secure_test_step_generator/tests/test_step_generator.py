from ..models import CursorHint, SanitizedEvidenceItem
from ..step_generator import generate_test_steps


class FakeLLMProvider:
    def __init__(self, response):
        self.response = response
        self.last_prompt = None

    def generate(self, prompt):
        self.last_prompt = prompt
        return self.response


def _evidence(order=0, notes="Notes here", ocr="OCR text here", cursor=None):
    return SanitizedEvidenceItem(
        order=order,
        sanitized_notes=notes,
        sanitized_ocr_text=ocr,
        cursor_hint=cursor,
        source_ref=f"paragraph {order}",
    )


def test_generates_one_step_per_evidence_item_on_well_formed_response():
    provider = FakeLLMProvider(
        {
            "steps": [
                {
                    "step_no": 1,
                    "action": "Click Submit on the claim intake screen",
                    "expected_result": "Claim is submitted and confirmation shown",
                    "confidence": 0.84,
                    "confidence_reason": "OCR quality high; cursor detected",
                    "warnings": [],
                }
            ]
        }
    )
    steps = generate_test_steps([_evidence()], provider)

    assert len(steps) == 1
    assert steps[0].step_no == 1
    assert steps[0].action == "Click Submit on the claim intake screen"
    assert steps[0].confidence == 0.84
    assert steps[0].warnings == []
    assert steps[0].status == "GENERATED"


def test_out_of_range_confidence_is_clamped_with_warning():
    provider = FakeLLMProvider(
        {"steps": [{"action": "A", "expected_result": "B", "confidence": 1.5}]}
    )
    steps = generate_test_steps([_evidence()], provider)

    assert steps[0].confidence == 1.0
    assert any("clamped" in w for w in steps[0].warnings)


def test_negative_confidence_is_clamped_to_zero_with_warning():
    provider = FakeLLMProvider(
        {"steps": [{"action": "A", "expected_result": "B", "confidence": -0.3}]}
    )
    steps = generate_test_steps([_evidence()], provider)

    assert steps[0].confidence == 0.0
    assert any("clamped" in w for w in steps[0].warnings)


def test_boolean_confidence_is_treated_as_unusable_not_as_0_or_1():
    provider = FakeLLMProvider(
        {"steps": [{"action": "A", "expected_result": "B", "confidence": True}]}
    )
    steps = generate_test_steps([_evidence()], provider)

    assert steps[0].confidence == 0.0
    assert any("did not return a usable confidence" in w for w in steps[0].warnings)


def test_missing_step_in_response_gets_conservative_placeholder_with_warning():
    provider = FakeLLMProvider({"steps": []})
    steps = generate_test_steps([_evidence(), _evidence(order=1)], provider)

    assert len(steps) == 2
    for step in steps:
        assert step.confidence == 0.0
        assert any("requires manual authoring" in w for w in step.warnings)


def test_malformed_response_does_not_raise():
    provider = FakeLLMProvider({})
    steps = generate_test_steps([_evidence()], provider)

    assert len(steps) == 1
    assert steps[0].confidence == 0.0


def test_empty_evidence_returns_empty_list_without_calling_llm():
    provider = FakeLLMProvider({"steps": []})
    steps = generate_test_steps([], provider)

    assert steps == []
    assert provider.last_prompt is None


def test_response_steps_out_of_array_order_are_matched_by_step_no_not_position():
    # The LLM is asked to echo step_no back, but nothing guarantees its
    # JSON array preserves evidence order. Matching purely by array
    # position would silently attach evidence[0]'s screenshot to
    # evidence[1]'s action/expected_result whenever the model reorders --
    # a correctness bug for a tool whose whole point is accurate
    # evidence-to-step mapping.
    provider = FakeLLMProvider(
        {
            "steps": [
                {
                    "step_no": 2,
                    "action": "Click confirm on the second screen",
                    "expected_result": "Confirmation shown",
                    "confidence": 0.9,
                },
                {
                    "step_no": 1,
                    "action": "Click submit on the first screen",
                    "expected_result": "Form submitted",
                    "confidence": 0.9,
                },
            ]
        }
    )
    steps = generate_test_steps([_evidence(order=0), _evidence(order=1)], provider)

    assert steps[0].step_no == 1
    assert steps[0].action == "Click submit on the first screen"
    assert steps[1].step_no == 2
    assert steps[1].action == "Click confirm on the second screen"


def test_confidence_reason_returned_as_list_is_joined_into_a_string_with_warning():
    # The prompt asks for "1-3 bullet-style reasons", which real models
    # sometimes return as a JSON list rather than a single string. TestStep
    # is typed as str, and downstream validator.py calls .strip()/regex
    # substitution on confidence_reason -- a list there crashes the pipeline.
    provider = FakeLLMProvider(
        {
            "steps": [
                {
                    "action": "A",
                    "expected_result": "B",
                    "confidence": 0.8,
                    "confidence_reason": ["OCR quality high", "cursor detected"],
                }
            ]
        }
    )
    steps = generate_test_steps([_evidence()], provider)

    assert steps[0].confidence_reason == "OCR quality high; cursor detected"
    assert any("please double-check it reads correctly" in w for w in steps[0].warnings)


def test_action_returned_as_non_string_is_coerced_with_warning():
    provider = FakeLLMProvider(
        {"steps": [{"action": 42, "expected_result": "B", "confidence": 0.8}]}
    )
    steps = generate_test_steps([_evidence()], provider)

    assert steps[0].action == "42"
    assert any("unexpected format" in w for w in steps[0].warnings)


def test_prompt_includes_placeholders_and_cursor_hint_not_raw_values():
    provider = FakeLLMProvider({"steps": [{}]})
    evidence = _evidence(
        notes="Claimant ID: <CLAIMANT_ID>",
        ocr="Employer: <EMPLOYER_ID>",
        cursor=CursorHint(description="near Submit button", confidence=0.7),
    )
    generate_test_steps([evidence], provider)

    assert "<CLAIMANT_ID>" in provider.last_prompt
    assert "<EMPLOYER_ID>" in provider.last_prompt
    assert "near Submit button" in provider.last_prompt

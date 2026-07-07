#governance/output_validator.py


class OutputValidationError(Exception):
    """
    Raised when a Skill's AI output fails its own output contract.

    This is a governance-recognized *category* of failure (distinct
    from an agent crashing), not a domain judgment. Governance only
    needs to know "the contract was violated"; deciding *what the
    contract requires* (which keys, which shape) is entirely up to
    each agent's own validate_result() override.
    """


def is_non_empty_mapping(result) -> bool:
    """
    Minimal, domain-neutral default contract: the LLM must have
    returned a non-empty dict. This exists specifically to close the
    silent failure mode where a malformed/unparseable LLM response
    is coerced to `{}` and then flows downstream as if it were a
    legitimate (if empty) result.
    """
    return isinstance(result, dict) and bool(result)

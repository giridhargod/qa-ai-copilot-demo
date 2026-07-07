#governance/retry_policy.py
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetryPolicy:
    """
    Governance-level decision about whether a failed step is worth
    retrying. Deliberately provider-agnostic: this module has no
    knowledge of OpenAI or any other LLM SDK's exception types. The
    caller supplies which exception types count as transient (e.g.
    rate limits, timeouts, connection drops) when constructing the
    policy, keeping any provider-specific knowledge in the service
    layer, not in Governance.

    Retrying nothing (the default) is a safe, explicit starting
    point — a step either succeeds or fails outright until a caller
    opts in to specific transient exception types.
    """

    max_attempts: int = 1
    transient_exceptions: tuple = field(default_factory=tuple)

    def is_transient(self, exc: Exception) -> bool:
        return isinstance(exc, self.transient_exceptions)

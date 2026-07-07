# Wave 2 — Workflow Governance Layer (Human-Review / Validation Gate)

Status: **Implemented, tested, and documented; awaiting commit.** Approved 2026-07-08.

See `docs/waves/README.md` for what this file is and what each section means.

---

## 1. Scope

**Approved:** build the reusable Workflow Governance runtime that (a) lets the workflow halt when a Skill/Critic's verdict says it should, (b) handles agent failures and AI output validation gracefully instead of crashing or silently swallowing bad data, and (c) does all of this as small, independently testable components future Skills can plug into without modifying the orchestrator.

**Explicitly excluded from this wave** (see §8 for why):
- Resumable/suspendable workflows (persisting a paused run for a human to later act on) — depends on the still-unresolved persistence decision (`MASTER_CONTEXT.md` §6 decision #9).
- Wiring a second gate onto the `CriticAgent`'s testcase verdict — the pattern now exists and is cheap to add, but wasn't needed to prove the governance layer works.
- Any `test_design/` implementation — unrelated to this wave; still empty stubs.
- Per-agent `validate_result()` overrides beyond the shared default — no agent's gate currently depends on specific required keys, so stricter contracts weren't invented speculatively.
- Fixing the pre-existing `tests/test_imports.py` pytest-collection warning, or the Streamlit `use_container_width` deprecation warnings — both noticed during this wave, neither caused by it.

---

## 2. Files Changed

**New — `governance/` package (the runtime; contains zero domain-specific rules):**
- `governance/__init__.py`, `governance/status.py` (`WorkflowStatus` enum), `governance/contracts.py` (`GateDecision`), `governance/retry_policy.py` (`RetryPolicy`), `governance/execution_guard.py` (`ExecutionGuard`, `ExecutionOutcome`), `governance/output_validator.py` (`OutputValidationError`, `is_non_empty_mapping`), `governance/gate_engine.py` (`GateEngine`), `governance/workflow_step.py` (`WorkflowStep`).

**Modified — data model:**
- `models/execution_record.py` — added `error_message: str | None = None`.
- `models/workflow_state.py` — added `status: WorkflowStatus`, `status_reason: str`.

**Modified — agents & critics (business logic, unchanged responsibilities, new hooks):**
- `agents/base_agent.py` — `BaseAgent.gate_check()` (default `None`), `LLMAgent.validate_result()` (default: non-empty dict), `LLMAgent.execute()` now raises `OutputValidationError` on a failed contract instead of silently storing bad output.
- `agents/requirement_readiness_agent.py` — `gate_check()` delegates to `RequirementReadinessCritic.to_gate_decision()`.
- `critics/requirement_readiness_critic.py` — new `to_gate_decision()` static method and `HARD_FAIL_CONFIDENCE = 40` constant; this is where the business interpretation of the verdict lives.

**Modified — service layer:**
- `services/openai_service.py` — new `TRANSIENT_EXCEPTIONS` constant (provider-specific retry whitelist), kept out of `governance/` to preserve LLM-agnosticism.

**Modified — orchestration & UI:**
- `workflows/workflow.py` — `self.agents` list replaced with `self.steps: list[WorkflowStep]`; loop now runs each step through `ExecutionGuard`, applies `WorkflowStep.critical` for graceful degradation, and consults `GateEngine` after each successful step; `state.status` is set to `RUNNING`/`FAILED_AGENT`/`FAILED_VALIDATION`/a gate's status/`COMPLETED` at the appropriate points.
- `app/streamlit_app.py` — branches on `result.status`; anything other than `COMPLETED` renders a warning/error banner with the governance reason and a reduced execution-log view, then `st.stop()`s before the full dashboard.
- `scripts/dev/smoke_workflow.py` — status-aware now; the old unconditional `len(critic_reviews) == 2` assertion only applies when the run actually completes.

**New tests:** `tests/test_governance_status.py`, `tests/test_execution_guard.py`, `tests/test_output_validation.py`, `tests/test_gate_engine.py`, `tests/test_requirement_readiness_gate.py`, `tests/test_workflow_gating.py`.

**Dependency hygiene:** `requirements.txt` — added `pytest` (it was already required to run the existing and new test suite but was undeclared).

---

## 3. Business Problem Solved

Wave 1 fixed the `critic_reviews` data-loss bug but left a bigger gap in place: the platform's own stated principle — *"Rules → AI → Validation → Human Review. Never AI → Final Answer"* — was not enforced anywhere in code. The deterministic Requirement Readiness Critic computed a real verdict (`approved`, `confidence`, `needs_sme`), and the workflow ran every downstream AI stage regardless of what it said. This wave makes that principle real: a rejected or SME-flagged requirement now halts before any further AI cost is spent on it, and does so through a reusable mechanism every future Skill inherits for free, rather than a one-off special case bolted onto `workflow.py`.

---

## 4. Why Each File/Component Changed

- **`governance/status.py` / `governance/contracts.py`** — a shared vocabulary (`WorkflowStatus`) and a single contract (`GateDecision`) for Skills to talk to the runtime. `GateDecision` self-validates (`proceed=False` must carry a halting status) so a Skill can't hand Governance an internally inconsistent instruction.
- **`governance/retry_policy.py`** — deliberately knows nothing about OpenAI or any provider; the caller supplies which exception types are transient. This keeps the platform's "LLM-agnostic" stable decision intact even inside the retry mechanism.
- **`governance/execution_guard.py`** — replaces the old unconditional `ExecutionRecord(status="SUCCESS")` with an honest outcome: catches exceptions, retries only what the policy says is transient, and classifies `OutputValidationError` as `FAILED_VALIDATION` (never retried — a content problem, not a network blip) versus everything else as `FAILED_AGENT` (retried per policy, then failed).
- **`governance/output_validator.py`** — closes a concrete, previously silent bug: `OpenAIService.extract_json()` returns `{}` on malformed/unparseable LLM output, and that empty dict used to flow downstream as if it were a legitimate result. Now it's caught at the agent boundary.
- **`governance/gate_engine.py` / `governance/workflow_step.py`** — the actual extension point. `GateEngine` only ever asks `agent.gate_check(state)` and applies the answer; it never reads `confidence`, `approved`, or any other business field. `WorkflowStep.critical` is the graceful-degradation seam for future optional Skills (e.g. SME Escalation, AI Chat) — unused by any current step (all five remain critical), but costs nothing to have in place.
- **`agents/base_agent.py`** — `gate_check()` added to `BaseAgent` (not just `LLMAgent`) since `RequirementReadinessAgent` extends `BaseAgent` directly. Default `None` means every existing agent participates in the same contract with zero code change required from them.
- **`critics/requirement_readiness_critic.py`** — `to_gate_decision()` is where `confidence`/`approved`/`needs_sme` actually get interpreted into a workflow-control decision. This is intentionally *not* in `governance/`: Governance executes decisions, Critics make them.
- **`workflows/workflow.py`** — the loop now iterates `WorkflowStep`s instead of raw agents; on any step failure it checks `critical` before deciding whether to halt or continue; on any step success it asks `GateEngine` before moving to the next step.
- **`app/streamlit_app.py`** — previously showed "Analysis Completed" and a full dashboard regardless of what actually happened. Now genuinely reflects outcome.
- **`scripts/dev/smoke_workflow.py`** — its hard 2-critic assertion assumed the pipeline always reaches the end, which stopped being a safe assumption the moment a legitimate gate could halt it earlier.

---

## 5. Engineering Principles Applied

- **#5 Modular Architecture** (`ENGINEERING_PRINCIPLES.md`) — Governance split into 5 single-responsibility components (status, contracts, retry policy, execution guard, gate engine) rather than one large class, per explicit Architect direction this wave.
- **#6 Knowledge Separation** — business thresholds (`HARD_FAIL_CONFIDENCE`) live with the Critic, not the runtime; provider-specific exception types live in the service layer, not the runtime.
- **"Rules → AI → Validation → Human Review"** (`CLAUDE.md`) — this wave is the first point in the codebase where this is actually enforced in code, not just stated.
- **"Design graceful degradation wherever practical"** — `WorkflowStep.critical` + `ExecutionGuard`'s retry/failure classification directly implement this for the first time.
- **#13 Measure Quality** — every new component shipped with unit tests exercising it in isolation (no live API calls needed to prove the gate, the guard, or the validator work).

---

## 6. Architecture Principles Applied

- **"Workflows orchestrate, never implement business logic"** (`ARCHITECTURE.md`) — `workflow.py` only ever calls `ExecutionGuard.run()` and `GateEngine.evaluate()`; it contains no confidence thresholds or verdict-field inspection.
- **"AI never bypasses deterministic validation"** — now enforced end-to-end: a rejected readiness verdict halts the pipeline before any AI stage runs.
- **"Human Review remains available throughout the platform"** — the gate mechanism (`gate_check()` on any `BaseAgent`) is not special-cased to Requirement Readiness; any future Skill can request a pause the same way.
- **"LLM-agnostic"** — `governance/` has zero imports of `openai` or any provider SDK; that knowledge stays in `services/openai_service.py`.
- **"Components should avoid circular dependencies"** — dependency direction is strictly one-way: `critics/` and `agents/` depend on `governance/`; `governance/` depends on nothing in `agents/`, `critics/`, or `services/` except the neutral `models.ExecutionRecord` and `services.TimeService`.

---

## 7. Relevant Anthropic / CCAF Concepts

- **Decisions vs. execution as a multi-agent design pattern**: `GateDecision` is a minimal, purpose-built contract — the smallest shape that lets a decision-making component (a Critic) and an execution-enforcing component (Governance) communicate without either needing to know the other's internals. This is the same "keep agent/tool contracts narrow" principle Wave 1's `LLMAgent` extraction demonstrated, applied one layer up — at the workflow-control level instead of the agent-execution level.
- **Testing multi-agent control flow without live model calls**: every governance test (guard, gate, validator, and the four end-to-end `test_workflow_gating.py` scenarios) uses fakes/mocks instead of a real LLM call. Proving "the pipeline halts correctly when the critic says so" doesn't require a real critic verdict — a deterministic, injectable seam (mocking `ReadinessService.analyze`) is what made the control flow itself testable in isolation from AI non-determinism.
- **Graceful degradation as a first-class design concern, not an afterthought**: `WorkflowStep.critical` exists before any non-critical Skill does, specifically so the *next* Skill that needs it doesn't require a framework change — this is "build the seam before you need the feature," a recognizable enterprise-agent-system pattern (separating what varies from what's fixed).

---

## 8. Trade-offs

- **Pause means "halt-and-return," not "suspend-and-resume."** A truly resumable paused workflow implies persisting `WorkflowState` somewhere a human can later act on it. Persistence (`MASTER_CONTEXT.md` §6 decision #9) is still unresolved and SQLite is confirmed dead, so this wave stops at: the orchestrator halts early, returns a `WorkflowState` explaining why, and the UI renders that instead of partial/misleading results. This is a real limitation, not an implied "true async human-in-the-loop" — full resume is natural Wave 3+ scope once #9 is decided. Notably, `docs/ARCHITECTURE.md`'s existing "Human Review Architecture" section already describes the target behavior as "pause... and allow execution to continue once resolved" — this wave delivers the pause half only; the "continue once resolved" half is the gap that remains.
- **`HARD_FAIL_CONFIDENCE = 40` is a business threshold I set as a working default**, not one the Architect specified. It's isolated to one named constant in `critics/requirement_readiness_critic.py` specifically so it's trivial to tune or override without touching Governance.
- **Only the Requirement Readiness step is gated in this wave.** The `CriticAgent`'s testcase verdict could use the identical pattern, but wasn't wired up — no current consumer needed it, and adding it speculatively would have meant inventing thresholds for a verdict nobody's asked to gate yet.
- **`critic_reviews`'s free-string keys (flagged in Wave 1) were not converted to an enum this wave**, even though `RequirementReadinessCritic.to_gate_decision()` now reads `state.critic_reviews.get("requirement_readiness", {})` by string key — this is the exact trigger condition Wave 1 named for revisiting it, but converting it wasn't required to ship a working gate. Flagged again here, more urgently, in §14.

---

## 9. Alternatives Considered

**Where should Gate rule logic live?** (see also `ARCHITECTURE_DECISIONS.md` ADR-004)
1. Inside `workflows/governance.py`, colocated with the orchestrator — rejected: puts business-threshold interpretation inside the Workflow layer, which `ARCHITECTURE.md` explicitly says never implements business logic.
2. A generic `CriticGate(verdict_key=..., thresholds=...)` class inside Governance, parameterized per-Skill — this was my initial proposal; rejected after Architect feedback because Governance would still be reaching into business-specific fields (`confidence`, `needs_sme`) by name, even if configured externally.
3. **Chosen:** the Critic itself exposes `to_gate_decision()`; the Agent's `gate_check()` hook delegates to it; Governance's `GateEngine` only ever sees the resulting `GateDecision`. This is the only option where Governance is provably domain-blind — it never imports or inspects a business field.

**Where should the `governance/` package sit relative to existing directories?**
1. Fold into `critics/` (my original proposal) — rejected on reflection: `critics/` is a business-logic package (verdicts about quality), while the guard/retry/gate-engine mechanics are pure runtime plumbing with no opinions of their own. Mixing them would blur exactly the seam this wave exists to draw.
2. **Chosen:** a new top-level `governance/` package. This does lightly touch pending decision #7 (formal directory-to-layer mapping) earlier than planned — accepted because `ARCHITECTURE.md`'s existing Workflow Layer description already names "approvals" and "auditability" as its responsibilities; `governance/` is the concrete implementation of responsibilities already assigned to that layer, not a brand-new 8th layer requiring fresh architectural sign-off.

---

## 10. Verification Performed

- **Unit tests, no live API calls:** `WorkflowStatus`/`GateDecision` invariants (`test_governance_status.py`), `ExecutionGuard` retry/failure classification against fake agents (`test_execution_guard.py`), `LLMAgent.validate_result()`/`OutputValidationError` propagation (`test_output_validation.py`), `GateEngine`'s mechanical pass-through behavior (`test_gate_engine.py`), and `RequirementReadinessCritic.to_gate_decision()`'s threshold logic across all four outcomes (`test_requirement_readiness_gate.py`).
- **End-to-end orchestrator tests** (`test_workflow_gating.py`): the real `WorkflowOrchestrator`, with only `ReadinessService.analyze` mocked, correctly reaches `COMPLETED`, `NEEDS_SME`, `FAILED_VALIDATION`, and `PAUSED_FOR_REVIEW` — and in the three halting cases, `state.ui_analysis` stays `{}`, proving no AI step ran after the gate fired.
- **Full suite:** 38/38 tests passing (17 pre-existing + 21 new).
- **Manual exception-path check:** a stub agent that raises `RuntimeError` mid-run was substituted into a live `WorkflowOrchestrator` — confirmed the run halts with `FAILED_AGENT` and an honest `execution_log` instead of crashing the process.
- **UI verification (per this project's standing practice of testing UI changes live, not just by reading the diff):** no `chromium-cli`/Playwright available in this environment, so verified via Streamlit's own `AppTest` headless harness — confirmed cold boot renders with zero exceptions; confirmed a mocked `NEEDS_SME` state renders the new warning banner and **not** the old "Analysis Completed" success path (`st.stop()` correctly short-circuits); confirmed a mocked `COMPLETED` state still renders the full 10-tab dashboard unchanged (no regression to the happy path).

---

## 11. Risks Introduced or Removed

**Removed**
- Silent ignoring of the readiness critic's verdict — the platform's central "Rules → AI → Validation → Human Review" claim is now true in code, not just in `CLAUDE.md`.
- Uncaught exceptions in any agent step crashing the entire workflow process.
- Malformed/empty LLM output (`extract_json()` → `{}`) silently flowing downstream as if valid.
- The Streamlit UI claiming "Analysis Completed" regardless of actual outcome.

**Introduced**
- `HARD_FAIL_CONFIDENCE = 40` is an engineering-chosen default standing in for a business decision — low risk (isolated, named, one line to change) but should be confirmed or overridden by the Architect/Product Owner.
- `critics/requirement_readiness_critic.py` now reads `state.critic_reviews` by the same free-string key (`"requirement_readiness"`) Wave 1 flagged as technical debt — the risk hasn't grown in kind, but this wave is arguably the point that should have triggered the enum conversion (see §14).
- `WorkflowStep.critical` defaults to `True` and no current step sets it to `False` — the graceful-degradation path is implemented but untested against a *real* non-critical step scenario (only implicitly, via the `critical=True` path being exercised). Low risk since it's a simple boolean branch, but worth a dedicated test once a real non-critical Skill exists.

---

## 12. Rollback Strategy

All changes are in-memory/code-only — `WorkflowState` is not persisted, so there is no data migration in either direction. Reverting this wave's commit(s) fully restores Wave 1's behavior: the unconditional agent loop, hardcoded `"SUCCESS"` execution records, and the ignored readiness verdict. No follow-up cleanup required either way.

---

## 13. Review Lesson

A "governance layer" request can easily balloon into a speculative framework (full state machines, persistence, resumable workflows) before any of it is needed. The discipline that kept this wave scoped was treating "what does today's five-agent, one-gate workflow actually require" as the hard boundary, while still designing the seams (`WorkflowStep.critical`, the `gate_check()` hook available to every `BaseAgent`) so the *next* requirement doesn't need a redesign — building extension points is not the same thing as building the extension.

---

## 14. Future Improvements

- **Convert `critic_reviews`'s free-string keys to an enum/constant set.** Flagged in Wave 1 as "revisit if a third critic is added"; this wave's `to_gate_decision()` reading `"requirement_readiness"` by string is arguably already past that trigger point, since a typo here would now silently disable the gate (always defaulting to an empty dict → an automatic halt, which fails safe — but still worth closing properly).
- **Wire the same `gate_check()` pattern onto `CriticAgent`'s testcase verdict** once there's an actual need to gate on it (e.g. alongside a Test Design wave).
- **Add a dedicated test exercising `WorkflowStep.critical=False`** once a real non-critical Skill exists, rather than relying on the boolean branch's simplicity as sufficient coverage.
- **Resolve persistence (`MASTER_CONTEXT.md` §6 decision #9)**, which unlocks true suspend/resume — the "continue once resolved" half of `ARCHITECTURE.md`'s own Human Review Architecture section, still unimplemented.
- **Confirm or override `HARD_FAIL_CONFIDENCE = 40`** — an engineering default standing in for a Product Owner decision.
- Carried over, unaffected by this wave: `requirements.txt`/doc-corruption root cause (recurred during this session — see the flagged incident above), `services/requirement_intelligence_service.py`'s fate, `test_design/`'s fate, remaining pending architecture decisions in `MASTER_CONTEXT.md` §6.

---

## 15. Proposed `MASTER_CONTEXT.md` Updates

Applied this session (see `MASTER_CONTEXT.md` directly for the resulting text) — summarized here per convention:

**Added**
- Wave 2 marked complete; Workflow Governance Layer (`governance/` package) documented as real, wired infrastructure in §3.
- Pending decision #2 (human-review/validation gate design) marked **resolved** for the "halt" half; the "resume" half now explicitly tracked as dependent on decision #9.
- New note under §3 that `WorkflowState.status`/`status_reason` now reflect real execution outcome, and `ExecutionRecord.status` is no longer hardcoded.

**Changed**
- §0/§4 current milestone updated to reflect Wave 2 complete, Wave 3 not yet chosen.
- §6 decision #3 (verdict reconciliation) further narrowed: independent-gate-per-producer is now the working answer for "how do multiple verdicts interact," rather than a fully open question.

**Removed**
- Wave 2 line item removed from the "Implementation queue."

**Why the change is required:** same reasoning as Wave 1's ADR-003 — leaving `MASTER_CONTEXT.md` unedited after this session would misstate a since-resolved question (the ignored-verdict gap) as still open for the next session.

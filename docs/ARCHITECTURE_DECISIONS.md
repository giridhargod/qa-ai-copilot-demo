Decision ADR-001: Product Vision and Engineering Principles are foundational documents. They should evolve only when there is a significant architectural reason. Routine feature work should not modify them.

---

## ADR-002: Critic Data Contract Repair — `critic_review` → `critic_reviews`

**Date:** 2026-07-07
**Status:** Decided and implemented (commit `236259c`).
**Requires Product Owner approval:** Yes — approved (Wave 1 sign-off).

**Context:** `WorkflowState.critic_review` was a single field, written by both the deterministic Requirement Readiness critic and the AI `CriticAgent`. Whichever agent ran second silently overwrote the other's verdict, with no error and no test catching it — a real data-loss bug, flagged as a known issue during Wave 1 planning but explicitly deferred pending an architecture decision on how the two verdicts should coexist (original pending decision #3).

**Alternatives considered:**
1. **Wait for the full reconciliation-UX decision** before touching `WorkflowState` at all — keeps scope minimal but leaves a known data-loss bug live indefinitely with no target date.
2. **Merge both verdicts into one combined verdict now** (e.g. AND their approval flags, or produce a synthesized summary) — solves data loss but *is* the reconciliation-UX decision, made unilaterally by the Implementation Engineer rather than the Architect/Product Owner; risks pre-empting a decision that affects how reviewers actually read the tool's output.
3. **Namespace by producer identity: `critic_reviews: dict[str, dict]` keyed by critic name** — stops the overwrite with a minimal, reversible structural change, without deciding how a human should read two verdicts together.

**Decision:** Option 3. Replaced `critic_review: dict` with `critic_reviews: dict`, keyed by `"requirement_readiness"` and `"testcase"`. Both agents write to their own key; the UI now renders both.

**Reasoning:** this fixes the correctness bug (silent data loss) — which is unambiguously a bug, not a design question — without deciding the open design question (how should a reviewer interpret two verdicts side by side). Separating "stop losing data" from "design the reconciliation UX" let the bug close now instead of waiting on a decision that has no committed timeline.

**Trade-offs:**
- Keys are free-form strings, not an enum — a future third critic with a typo'd key would silently create an orphaned entry rather than raising an error. Accepted as low risk with two producers and test coverage (`tests/test_critic_reviews.py`); revisit if a third critic is added.
- Does not solve the UX question of how a reviewer should weigh two independent verdicts (e.g., what if they disagree?) — that half of the original decision remains open.

**Implementation impact:** `models/workflow_state.py`, `agents/critic_agent.py`, `agents/requirement_readiness_agent.py`, `app/streamlit_app.py`, `scripts/dev/smoke_workflow.py` changed; `tests/test_critic_reviews.py` added. Full file-level detail: `docs/waves/WAVE_1.md` §4, §9.

---

## ADR-003: Engineering Documentation Structure — Wave Records vs. Cross-Wave Learning Log

**Date:** 2026-07-07
**Status:** Decided and implemented (commit `3b84d25`).
**Requires Product Owner approval:** Yes — approved after review (Giri selected "Implement now" after the alternatives below were presented).

**Context:** Giri asked for two new recurring documentation practices going forward: (1) a reusable "Engineering Knowledge Base" per wave (files changed, business problem, why, principles, trade-offs, verification, risks, rollback, review lessons) and (2) a "CCAF/Engineering Learning Map" per wave (CCAF concepts, enterprise architecture, AI engineering, QA engineering, Python, interview value, alternatives-not-chosen, where else the pattern recurs). Both were requested as new artifacts. Before creating anything, the existing `docs/` structure was reviewed: `docs/IMPLEMENTATION_CHANGES.md` (Wave 1's record) already covered ~6 of 9 requested sections for proposal 1, and `docs/LESSONS_LEARNED.md` (an existing, half-filled, never-completed draft) already covered proposal 2's intent loosely, and `docs/CLAUDE.md`'s "Learning Companion Responsibilities" section already mandated the substance of proposal 2 as stated philosophy.

**Alternatives considered:**
1. **Create two new top-level docs** (e.g. `docs/ENGINEERING_KNOWLEDGE_BASE.md`, `docs/CCAF_LEARNING_MAP.md`) as literally requested — straightforward, but would create three parallel places (`IMPLEMENTATION_CHANGES.md` + two new docs) independently narrating "why we did X" for the same wave, with no mechanism to keep them in sync — the exact staleness/drift failure mode `MASTER_CONTEXT.md` itself warns about.
2. **Cram everything into one ever-growing `MASTER_CONTEXT.md`** — rejected outright: `MASTER_CONTEXT.md` is explicitly scoped as a *current-state snapshot*, not a historical log, and ADR-001 already treats foundational-doc scope creep as something to actively avoid.
3. **Two-layer structure: per-wave detail files + one curated cross-wave synthesis file** — `docs/IMPLEMENTATION_CHANGES.md` renamed/extended into `docs/waves/WAVE_N.md` (one file per wave, written once, never rewritten — preserves what was actually known/decided at the time) plus `docs/LESSONS_LEARNED.md` rebuilt into the curated, tagged, cross-wave revision guide, cross-linking back to its source wave rather than re-deriving the same narrative.

**Decision:** Option 3.

**Reasoning:** the two proposed artifacts overlap almost entirely in content with what already existed; the real gap was a missing *convention* (how to name/organize per-wave files so they scale past Wave 1) and a missing *curation step* (promoting only the generalizable patterns into a revision guide, instead of dumping full wave detail into it). Solving those two gaps satisfies both of Giri's proposals without introducing document drift.

**Trade-offs:**
- Slightly less literal a match to the original request's exact document names — mitigated by explaining the reasoning and getting explicit sign-off before implementing, rather than silently substituting a different structure.
- Requires discipline to keep `LESSONS_LEARNED.md` curated (only 1–3 patterns promoted per wave) rather than letting it become a second copy of the wave file — this is a process risk, not a structural one; called out explicitly in `docs/LESSONS_LEARNED.md`'s own header.

**Implementation impact:** `docs/IMPLEMENTATION_CHANGES.md` → `docs/waves/WAVE_1.md` (git-mv, preserves history); `docs/waves/README.md` added (template/convention); `docs/LESSONS_LEARNED.md` rebuilt with a tagged-entry format. All previously-uncommitted `docs/*.md` scaffolding committed alongside as a documentation checkpoint. Full detail: `docs/waves/WAVE_1.md` (historical, frozen) — this ADR is the authoritative record of the decision itself going forward.

---

## ADR-004: Workflow Governance Layer — Human-Review Gate as Reusable Runtime

**Date:** 2026-07-08
**Status:** Decided and implemented (Wave 2, pending commit).
**Requires Product Owner/Architect approval:** Yes — approved (design reviewed and Wave 2 scope confirmed before implementation began).

**Context:** Wave 1 fixed `critic_reviews`'s data-loss bug but left the underlying gap untouched: `RequirementReadinessAgent` computed a real deterministic verdict (`approved`, `confidence`, `needs_sme`), and `workflow.py` ran every downstream AI stage regardless of it. The platform's stated principle — "Rules → AI → Validation → Human Review. Never AI → Final Answer" — was fiction in the code. This was raised as the top finding of a Wave 2 readiness review and approved as Wave 2's scope, reframed from "add a pause feature" to "build the reusable Workflow Governance runtime every future Skill plugs into."

**Decisions made, each requiring its own resolution:**

**(A) Scope: halt-and-return vs. suspend-and-resume.** A truly resumable paused workflow requires persisting `WorkflowState` somewhere a human can act on it later; persistence (pending decision #9) is unresolved and SQLite is confirmed dead. **Decided:** halt-and-return only — the orchestrator stops early and returns a `WorkflowState` explaining why; no queue, no resume action, no override status. `ARCHITECTURE.md`'s existing "Human Review Architecture" section already names both halves ("pause... and allow execution to continue once resolved"); this wave delivers only the first half, explicitly deferring the second to whenever decision #9 is resolved.

**(B) Where Gate rule logic lives.** Three options considered:
1. `workflows/governance.py`, colocated with the orchestrator — rejected: puts business-threshold interpretation inside the Workflow layer, contradicting the stable decision "workflows orchestrate, never implement business logic."
2. A generic `CriticGate(verdict_key=..., thresholds=...)` class living in Governance, configured per-Skill — this was the initial proposal, but still has Governance reaching into named business fields (`confidence`, `needs_sme`), just via configuration instead of hardcoding. Rejected after Architect feedback: "Skills and Critics make decisions; Governance only executes them."
3. **Chosen:** the Critic itself exposes `to_gate_decision(review_result) -> GateDecision` (`critics/requirement_readiness_critic.py`); the Agent's `gate_check(state)` hook (added to `BaseAgent`, default `None`) delegates to it; Governance's `GateEngine` only ever sees the resulting neutral `GateDecision`, never a business field.

**(C) Where the `governance/` package sits.** Considered folding into `critics/` (reuse an existing directory) — rejected: `critics/` holds business-logic verdicts, while the guard/retry/gate-engine mechanics are domain-blind runtime plumbing; mixing them blurs the seam this wave exists to draw. **Decided:** a new top-level `governance/` package. This lightly touches pending decision #7 (formal directory-to-layer mapping) earlier than planned, but `ARCHITECTURE.md`'s existing Workflow Layer description already names "approvals" and "auditability" as responsibilities of that layer — `governance/` is the concrete implementation of a responsibility already assigned, not an unplanned 8th layer.

**(D) Internal modularity.** Explicit Architect direction: no single large `Governance` class. **Decided:** five single-responsibility components — `WorkflowStatus`/`GateDecision` (contracts), `RetryPolicy`, `ExecutionGuard`, `OutputValidator`, `GateEngine`, `WorkflowStep` — each independently unit-testable without the others.

**Reasoning:** the common thread across (B), (C), and (D) is the same rule stated once and applied three times: Governance is a runtime that executes decisions, never one that makes them. Every design choice that would have blurred that line (parameterized thresholds in Governance, folding Governance into a business-logic directory, one large class owning both mechanics and judgment) was rejected in favor of the option that kept the boundary provable by inspection — Governance's source contains no confidence thresholds, no `needs_sme` checks, no OpenAI-specific exception types.

**Trade-offs:**
- `HARD_FAIL_CONFIDENCE = 40` (`critics/requirement_readiness_critic.py`) is an engineering-chosen default standing in for a Product Owner business decision — isolated to one named constant specifically so it's cheap to override.
- Only the Requirement Readiness step is gated this wave; the `CriticAgent`'s testcase verdict could use the identical pattern but wasn't wired up, since no current consumer needs it yet.
- `critic_reviews`'s free-string keys (flagged as debt in ADR-002) are now read programmatically by `to_gate_decision()` — arguably past the "revisit when a third critic arrives" trigger Wave 1 set, but not converted to an enum this wave (see `docs/waves/WAVE_2.md` §14).

**Implementation impact:** new `governance/` package (8 files); `models/execution_record.py`, `models/workflow_state.py`, `agents/base_agent.py`, `agents/requirement_readiness_agent.py`, `critics/requirement_readiness_critic.py`, `services/openai_service.py`, `workflows/workflow.py`, `app/streamlit_app.py`, `scripts/dev/smoke_workflow.py` changed; 6 new test files (38/38 tests passing). Full detail: `docs/waves/WAVE_2.md`.
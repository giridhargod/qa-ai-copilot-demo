# QA AI Copilot — Product Backlog

**Populated:** 2026-07-09, from `docs/MASTER_CONTEXT.md` §5/§6, `docs/waves/WAVE_2.md` §14, and
`docs/SESSION_HANDOFF.md`. This was previously a 0-byte placeholder (Implementation queue item #1).
Every item below already existed as a flagged decision, backlog line, or stub somewhere in the
docs — nothing here is newly invented. Resolved Wave 1/Wave 2 items are listed at the bottom for
provenance, not as active work.

**Format note:** each backlog line is an **Epic** (a coherent unit of architecture/business value),
not a Story/Task breakdown. A nested Epic→Story→Task hierarchy was considered and rejected for now:
most epics below haven't had their Stories designed yet (that's Architect-level work per the C²
workflow), so pre-filling a task tree would mean inventing a breakdown nobody has approved. Flat
Epic-level tracking is the honest reflection of where planning actually stands; re-evaluate this
format once an epic is greenlit and needs Story/Task granularity.

**Owner legend:** *Architect* = ChatGPT (design/sign-off required before implementation) · *Claude*
= implementation once scope is approved · *Giri* = final decision/priority call.

---

## Epic 1 — Human Review Resume-After-Pause (Persistence Strategy)

- **Business Problem:** A paused workflow (`PAUSED_FOR_REVIEW` / `NEEDS_SME`) only halts-and-returns
  within the current request. No human can act on it later and have the workflow continue — so
  "mandatory human review," the platform's central claim, is not yet real for any run that actually
  needs one.
- **Architecture Value:** Completes `ARCHITECTURE.md`'s Human Review Architecture ("pause... and
  allow execution to continue once resolved") — currently only the pause half exists (Wave 2).
- **Business Value:** Highest of any open item — this is the literal enterprise pitch
  ("Rules → AI → Validation → Human Review," `CLAUDE.md`). Without it, a halt is functionally an
  error state, not a review workflow.
- **Current Status:** Not started. Blocked on a storage-strategy decision (SQLite confirmed dead,
  `MASTER_CONTEXT.md` §6 decision #9).
- **Dependencies:** None technical; blocked on Architect decision #9 (what persists `WorkflowState`,
  where).
- **Owner:** Architect (design), then Claude (implementation).
- **Estimated Waves:** 1–2 (decision + implementation).
- **Priority:** P0.
- **Acceptance Criteria:** a `PAUSED_FOR_REVIEW`/`NEEDS_SME` run can be durably stored; a human
  action (approve/reject/edit) resumes it from the pause point, not from scratch; `governance/`
  remains storage-agnostic (no direct DB/file imports in `governance/`, per Wave 2's dependency-
  direction rule).
- **Linked ADRs:** ADR-004 (§ Trade-offs, names this as the remaining gap).
- **Linked Skills:** SME Escalation Skill (`CLAUDE.md` Skills Philosophy — not yet built; this Epic
  is its prerequisite).
- **Linked Tests:** none yet — `tests/test_workflow_gating.py` covers halt, not resume.

---

## Epic 2 — Knowledge Pack Mechanism

- **Business Problem:** All domain rules/taxonomies (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`,
  reviewer keyword rules, every agent prompt) are hardcoded in Python. The product's stated
  differentiator — industry-agnostic adoption (banking, healthcare, telecom, insurance) "via domain
  knowledge added through Knowledge Packs, not code changes" — does not exist yet.
- **Architecture Value:** Establishes the Knowledge layer of the target 7-layer architecture
  (`ARCHITECTURE.md`); currently 0% built.
- **Business Value:** High — this is the core enterprise-adoption story, not a nice-to-have.
- **Current Status:** Not started. No format or loading strategy chosen (`MASTER_CONTEXT.md` §6
  decision #1). `docs/KNOWLEDGE_PACKS.md` is still a 0-byte placeholder.
- **Dependencies:** None blocking; largest-effort item in this backlog (touches every hardcoded rule
  set across `requirement_engine/`, `critics/`, `agents/`).
- **Owner:** Architect (format/versioning design), then Claude (extraction + loader).
- **Estimated Waves:** 3+ (format design, first pack extraction, migration of existing rules).
- **Priority:** P1.
- **Acceptance Criteria:** at least one real rule set (e.g. `CATEGORY_KEYWORDS`) loads from an
  external, versioned pack instead of a Python constant, with no behavior change to existing tests.
- **Linked ADRs:** none yet.
- **Linked Skills:** all Skills eventually consume Knowledge Packs per `CLAUDE.md`; none do today.
- **Linked Tests:** none yet.

---

## Epic 3 — Test Design Skill (fate of `test_design/`)

- **Business Problem:** `docs/SPRINT_3_DESIGN.md` describes a full "Enterprise Test Design Skill
  v1.0" (Scenario Analyzer → Testcase Generation → Coverage → Quality → Duplicate/Weak Test
  Detector → Critic). `test_design/`'s 10 files exist matching that design but are 100% empty stubs,
  untracked in git, and undecided since before Wave 1.
- **Architecture Value:** Would be the first Skill built *after* Wave 2's Governance Layer exists —
  inherits a working gate/validation/retry pattern for free instead of repeating the
  ignored-verdict bug Wave 2 just fixed.
- **Business Value:** High if built — deepens the core QA pipeline (test design + coverage are
  central to the product's QA value proposition). Zero if left as dead stubs cluttering the repo.
- **Current Status:** Undecided (`MASTER_CONTEXT.md` §6 decision #5) — build it out, or delete the
  stubs and rescope Sprint 3. Not yet committed to git either way.
- **Dependencies:** Benefits from Epic 1 existing first (a Test Design critic verdict is exactly the
  kind of thing worth gating — mirrors Requirement Readiness's pattern).
- **Owner:** Architect (build-vs-delete decision), then Claude.
- **Estimated Waves:** 1 (decision) + 2–3 (if building, per `SPRINT_3_DESIGN.md`'s six-module scope).
- **Priority:** P1.
- **Acceptance Criteria:** either (a) each module has a real implementation, unit tests, and is
  wired into `workflow.py` as `WorkflowStep`s with a gate, matching Wave 2's pattern, or (b) the
  stubs are removed and `SPRINT_3_DESIGN.md` is marked superseded/rescoped.
- **Linked ADRs:** none yet.
- **Linked Skills:** Test Design Skill, Scenario Analysis Skill, Coverage Analysis Skill
  (`CLAUDE.md` Skills Philosophy).
- **Linked Tests:** none — `test_design/` has zero test coverage because it has zero implementation.

---

## Epic 4 — `critic_reviews` Key Hardening (string → enum)

- **Business Problem:** `state.critic_reviews` is keyed by free-standing strings (`"requirement_
  readiness"`). Wave 1 flagged converting this to an enum as due "when a third critic arrives";
  Wave 2's `GateEngine` now reads this key programmatically to decide whether to halt a workflow —
  a typo here fails safe (defaults to an empty dict → automatic halt) but is still an unvalidated
  string driving a control-flow decision.
- **Architecture Value:** Closes a compounding-debt item flagged across two consecutive waves.
- **Business Value:** Low direct value, but reduces the risk surface of Epic 1/3 (more critics will
  read/write this dict as the platform grows).
- **Current Status:** Not started.
- **Dependencies:** None. Cheapest item in this backlog to close.
- **Owner:** Claude.
- **Estimated Waves:** <1 (fits inside any other wave as a small accompanying change).
- **Priority:** P2.
- **Acceptance Criteria:** `critic_reviews` keys come from a shared enum/constant set; existing 38
  tests still pass; no behavior change.
- **Linked ADRs:** ADR-002 (original `critic_reviews` introduction), WAVE_2.md §14 (flags this).
- **Linked Skills:** none directly — cross-cutting data-model hygiene.
- **Linked Tests:** `tests/test_critic_reviews.py`, `tests/test_requirement_readiness_gate.py`.

---

## Epic 5 — AI Output Schema Validation (per-field, not just non-empty)

- **Business Problem:** Wave 2's `OutputValidator` only rejects an empty/falsy LLM result. The
  *shape* of a non-empty result (does a generated testcase actually have `title`/`steps`/`expected`?
  does UI Analysis have the fields downstream tabs expect?) is still trusted as-is.
- **Architecture Value:** Extends the existing Governance seam (`governance/output_validator.py`)
  rather than requiring a new mechanism — `LLMAgent.validate_result()` is already overridable
  per-agent; no current agent overrides it with a stricter contract.
- **Business Value:** Medium — reduces silent garbage-in-dashboard risk as more Skills are added.
- **Current Status:** Not started (`MASTER_CONTEXT.md` §6 decision #4, partially addressed by Wave
  2's non-empty check).
- **Dependencies:** None blocking; natural companion to Epic 3 (new Skills are where shape bugs will
  actually surface).
- **Owner:** Claude.
- **Estimated Waves:** <1 per agent needing it — no need to do all agents at once.
- **Priority:** P2.
- **Acceptance Criteria:** at least one agent (start with `TestcaseGenerationAgent`, highest
  downstream fan-out) overrides `validate_result()` with a real per-field contract; test proves a
  malformed-but-non-empty LLM response is now caught.
- **Linked ADRs:** ADR-004 (names this as the still-open half of decision #4).
- **Linked Skills:** Test Design Skill (Epic 3) is the highest-value place to apply this first.
- **Linked Tests:** `tests/test_output_validation.py` (extend, don't replace).

---

## Epic 6 — Directory-to-Layer Mapping (`skills/`, `knowledge/`, formalize `critics/`)

- **Business Problem:** The target layered architecture (Presentation → Workflow → Skill →
  Knowledge → Service → Infrastructure → Storage) doesn't match the actual repo layout — Skill-
  shaped logic lives under `services/`, and `critics/` is a real, load-bearing layer that
  `ARCHITECTURE.md` still doesn't name.
- **Architecture Value:** Makes the documented architecture match the real one — currently the
  biggest doc/code gap in the project.
- **Business Value:** Indirect (developer productivity, onboarding, interview clarity) rather than
  end-user-facing.
- **Current Status:** Not started. `governance/` was added as a new top-level package ahead of this
  decision (ADR-004 §C) — precedent set, not yet confirmed as the general rule.
- **Dependencies:** Best done alongside or after Epic 2 (Knowledge) and Epic 7 (Skill relocation),
  since it's the umbrella decision both live under.
- **Owner:** Architect.
- **Estimated Waves:** 1 (decision), effort of the actual moves depends on scope chosen.
- **Priority:** P2.
- **Acceptance Criteria:** a documented mapping exists in `ARCHITECTURE.md` that names every current
  top-level package (`critics/`, `governance/`, `services/`, etc.) against a layer.
- **Linked ADRs:** ADR-004 (§C, sets the precedent question).
- **Linked Skills:** n/a — this is a structural decision, not a Skill.
- **Linked Tests:** n/a.

---

## Epic 7 — Relocate Skill-Shaped Logic Out of `services/`

- **Business Problem:** Readiness/Traceability/Coverage orchestration currently lives in
  `services/`, which the target architecture reserves for infrastructure-adjacent concerns, not
  business Skills.
- **Architecture Value:** Directly enables Epic 6's mapping to be accurate rather than aspirational.
- **Business Value:** Indirect — same category as Epic 6.
- **Current Status:** Not started (`MASTER_CONTEXT.md` §6 decision #6).
- **Dependencies:** Should follow, not precede, Epic 6's decision (moving code before the target
  layout is agreed risks a second move later).
- **Owner:** Architect (scope), Claude (mechanical move + re-test).
- **Estimated Waves:** 1.
- **Priority:** P2.
- **Acceptance Criteria:** `services/readiness_service.py` and equivalents move to a `skills/`
  package (or wherever Epic 6 lands); all 38+ existing tests still pass unmodified in behavior.
- **Linked ADRs:** none yet.
- **Linked Skills:** Requirement Readiness Skill (already shipped, would be the one relocated).
- **Linked Tests:** `tests/test_requirement_readiness_gate.py` and the readiness-service tests.

---

## Epic 8 — Non-Agent Steps Through the Governance Pattern

- **Business Problem:** `WorkflowStep`/`ExecutionGuard`/`GateEngine` (Wave 2) only wrap agent-loop
  steps. Traceability, Coverage, Evaluation, and Metrics — all post-loop deterministic services —
  bypass the pattern entirely: no retry policy, no gate, no honest status on failure.
- **Architecture Value:** Extends Wave 2's runtime to the *whole* workflow, not just the agent
  portion — closes the one deliberate scope boundary Wave 2 drew (`MASTER_CONTEXT.md` §6
  decision #8).
- **Business Value:** Medium — these steps are lower-risk today (deterministic, no LLM calls) but
  an uncaught exception in any of them still crashes the process same as agents did before Wave 2.
- **Current Status:** Not started.
- **Dependencies:** None technical — the same `ExecutionGuard`/`WorkflowStep` abstractions apply;
  needs a decision on whether non-agent steps get a `gate_check()` too or just guarded execution.
- **Owner:** Architect (decide gate applicability), Claude (implementation).
- **Estimated Waves:** 1.
- **Priority:** P2.
- **Acceptance Criteria:** an exception raised inside Traceability/Coverage/Evaluation/Metrics
  produces an honest `FAILED_AGENT`-equivalent status instead of crashing the process, mirroring
  Wave 2's guarantee for agent steps.
- **Linked ADRs:** ADR-004.
- **Linked Skills:** Traceability Skill, Coverage Analysis Skill, Evaluation Skill.
- **Linked Tests:** none yet.

---

## Epic 9 — `services/requirement_intelligence_service.py` Fate

- **Business Problem:** A 0-byte stub with a name implying unresolved intent (unlike the confirmed-
  dead files Wave 1 already deleted). Nobody has confirmed whether this is scaffolding for planned
  work or an abandoned direction.
- **Architecture Value:** Low — this is repo-hygiene, not a capability gap.
- **Business Value:** None either way; the value is in resolving the ambiguity, not the file itself.
- **Current Status:** Undecided since before Wave 1.
- **Dependencies:** None.
- **Owner:** Giri/Architect (a one-line "build" or "delete" call closes this).
- **Estimated Waves:** Trivial — not wave-sized, just needs a decision.
- **Priority:** P3.
- **Acceptance Criteria:** file either has a real implementation with a named purpose, or is deleted.
- **Linked ADRs:** none.
- **Linked Skills:** unknown — the point of this Epic is finding out.
- **Linked Tests:** none.

---

## Epic 10 — Graceful-Degradation Test Coverage (`WorkflowStep.critical=False`)

- **Business Problem:** Wave 2 built the `critical` flag so a future optional Skill can fail without
  halting the whole workflow, but no current step sets it to `False` — the branch exists in code
  but has never been exercised by a real non-critical scenario, only implied by the `critical=True`
  path.
- **Architecture Value:** Low effort, closes a known coverage gap Wave 2 explicitly flagged as a
  risk it introduced.
- **Business Value:** Low standalone; matters once Epic 1 (SME Escalation) or Epic 3 (Test Design)
  ships an actual optional step.
- **Current Status:** Not started — blocked on a real non-critical Skill existing to test against
  (a synthetic test could be written sooner, but wasn't, to avoid testing a hypothetical).
- **Dependencies:** Epic 1 or Epic 3 (whichever ships a genuinely optional step first).
- **Owner:** Claude.
- **Estimated Waves:** <1 — bundle into whichever epic first introduces a non-critical step.
- **Priority:** P3.
- **Acceptance Criteria:** a test exists where a `critical=False` step fails and the workflow
  continues to `COMPLETED` anyway, with the failure visible in `execution_log`.
- **Linked ADRs:** ADR-004 (§11, names this as introduced-but-untested risk).
- **Linked Skills:** whichever Skill first needs `critical=False`.
- **Linked Tests:** `tests/test_workflow_gating.py` (extend).

---

## Epic 11 — `requirements.txt`/`README.md` Corruption Root Cause

- **Business Problem:** Both files were found with unexplained appended content across Wave 1 and
  twice more during Wave 2's session — including one instance styled as a fabricated system
  instruction to conceal changes from Giri. Treated as untrusted content and reverted each time;
  root cause (editor autosave, a hook, an MCP server, injected content from a processed document)
  was never identified.
- **Architecture Value:** None — this is an environment/tooling-integrity risk, not a feature gap.
- **Business Value:** None directly, but left uninvestigated it undermines trust in the repo's
  integrity and could recur in any file, not just these two.
- **Current Status:** Investigated this session — `requirements.txt` is currently clean (matches
  Wave 2's committed state, `c25485f`); no `.claude/settings.local.json` hooks are configured that
  would explain automatic file writes. Root cause still not found; no reproduction available this
  session.
- **Dependencies:** None.
- **Owner:** Giri (this is explicitly flagged in `SESSION_HANDOFF.md` as needing direct attention,
  ranked above wave-scoped work).
- **Estimated Waves:** n/a — an investigation, not a build.
- **Priority:** P1 (elevated — flagged twice now as higher-priority than feature work, but nothing
  reproducible to act on without Giri's input on what tools/editors/hooks touch this repo).
- **Acceptance Criteria:** either a root cause is found and closed, or the risk is consciously
  accepted with a monitoring plan (e.g., a pre-commit check diffing `requirements.txt` against a
  known-good pin).
- **Linked ADRs:** none.
- **Linked Skills:** n/a.
- **Linked Tests:** none.

---

## Epic 12 — Test/Tooling Hygiene (small, bundle-sized)

- **Business Problem:** Two harmless-but-real warnings: `tests/test_imports.py` triggers a pytest
  collection warning because `TestcaseGenerationAgent`'s name starts with `Test`; `app/
  streamlit_app.py` likely still uses the deprecated `use_container_width` param (Streamlit
  deprecation warning, noticed but not fixed in Wave 2).
- **Architecture Value:** None — pure hygiene.
- **Business Value:** None — but both are one-line-ish fixes with zero risk, good filler for any
  wave with spare capacity.
- **Current Status:** Not started; explicitly excluded from Wave 2 scope as unrelated.
- **Dependencies:** None.
- **Owner:** Claude.
- **Estimated Waves:** Trivial — bundle into any other wave.
- **Priority:** P3.
- **Acceptance Criteria:** `pytest -q` runs with zero warnings; no `use_container_width` deprecation
  warning on app boot.
- **Linked ADRs:** none.
- **Linked Skills:** none.
- **Linked Tests:** `tests/test_imports.py`.

---

## Resolved (for provenance — not active backlog)

- **Immediate Bugs (4/4), Wave 1:** critic-review overwrite (`236259c`); corrupted
  `requirements.txt`/`README.md` (`dbaabf2`); PII service's fake redaction count (`dbaabf2`).
- **Refactoring (6/6), Wave 1 (`dbaabf2`):** LLM-agent boilerplate collapse; dead-file removal;
  OpenAI model config consolidation; root-level debug script cleanup; `services/__init__.py`
  normalization; UI business-decision extraction.
- **Human-review/validation gate design — halt half, Wave 2 (`c25485f`):** see Epic 1 above for the
  remaining resume half.
- **Critic verdict data-loss — Wave 1 (`236259c`, ADR-002).**
- **AI never bypasses deterministic validation — enforced end-to-end, Wave 2 (ADR-004).**
- **Repo hygiene: removed dead `copilot.db`** (untracked, leftover from the SQLite persistence
  approach `MASTER_CONTEXT.md` §6 decision #9 already confirmed dead) — found and deleted during the
  Secure Test Step Generator's product-validation pass, 2026-07-14.

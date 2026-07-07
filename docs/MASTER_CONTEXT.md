# QA AI Copilot — Master Context

**Version 0.3 — Updated with Giri's explicit approval, 2026-07-08.**
Last generated: 2026-07-08, from Wave 2 (Workflow Governance Layer), implemented and documented, pending commit.

This is the primary onboarding document for any new Claude session working on QA AI Copilot. Read this before reading any other doc in `docs/`. It exists because the other docs (`ARCHITECTURE.md`, `SKILLS_GUIDE.md`, `WORKFLOW_GUIDE.md`, etc.) describe the **target** design in detail but do not say how much of it is actually built, nor what's in flight right now. This document draws that line.

For a short, scannable "start here" pointer before reading the rest of this file, see `docs/SESSION_HANDOFF.md`.

---

## 0. Current Status (as of end of session, 2026-07-08)

- **Milestone:** Workflow Governance Layer shipped — the platform's "Rules → AI → Validation → Human Review" principle is now enforced in code, not just stated.
- **Current wave:** **Wave 2 — Workflow Governance Layer (Human-Review / Validation Gate).** Status: **implemented, tested (38/38 passing), documented; pending commit.** Full record: `docs/waves/WAVE_2.md`; design decisions: `docs/ARCHITECTURE_DECISIONS.md` ADR-004.
- **Previous wave:** Wave 1 — Repository Cleanup, Agent Framework Improvements & Critic Data Contract Repair. Complete and committed (`dbaabf2`, `236259c`, `3b84d25`). Full record: `docs/waves/WAVE_1.md`.
- **Next wave:** **Not yet defined.** Per the C² workflow, Wave 3 scope is the Architect's/Giri's call. Candidates surfacing from Wave 2: converting `critic_reviews`'s free-string keys to an enum (see §6 decision #3 note below), resolving persistence (decision #9) to unlock resume-after-pause, or building out `test_design/` now that it would inherit a working gate instead of repeating the ignored-verdict pattern.
- **Open decisions:** 8 of the original 9 pending architecture decisions remain (§6) — decision #2 (human-review/validation gate design) is now **resolved** for the halt half; its resume half is folded into decision #9 (persistence).
- **Implementation queue (unordered, not yet prioritized):**
  1. Migrate the 24-item backlog into `docs/PRODUCT_BACKLOG.md` (currently empty).
  2. Resolve `services/requirement_intelligence_service.py`'s intent (build vs. delete).
  3. Decide the fate of `test_design/` (§6 decision #5) — Sprint 3 stubs, unimplemented.
  4. Convert `critic_reviews`'s free-string keys to an enum (Wave 1 debt, now read programmatically by Wave 2's gate — see `docs/waves/WAVE_2.md` §14).
  5. Any of the remaining 8 pending architecture decisions in §6, at the Architect's discretion.

---

## How to Update This Document

This file is not edited freely. After any completed implementation session:

1. Do **not** edit `MASTER_CONTEXT.md` directly.
2. Propose changes in this format:
   - **Added:** …
   - **Changed:** …
   - **Removed:** …
   - **Why the change is required:** …
3. Wait for Giri's (or the Architect's) explicit approval before applying the edit.

---

## 1. Product Vision (condensed)

QA AI Copilot is an Enterprise AI QA Platform, not a demo. It exists to help QA Engineers, SDETs, BAs, and QA Leads validate requirements, design tests, and track coverage/traceability — combining deterministic rule engines, AI reasoning, and mandatory human review. Target adoption is industry-agnostic (banking, healthcare, telecom, insurance, etc.) via domain knowledge added through Knowledge Packs, not code changes.

Core philosophy, stated identically across `CLAUDE.md`, `PRODUCT_VISION.md`, and `ENGINEERING_PRINCIPLES.md`:

> **Rules → AI → Validation → Human Review.** Never AI → Final Answer.

The project also has a **second, equally-weighted objective**: it is the primary vehicle for Giri's growth into an AI Engineer / Enterprise AI Architect / QA Architect. Every implementation is expected to produce both a working feature and a learning artifact (see §9).

---

## 2. Stable Architectural Decisions

These are treated as settled per `ARCHITECTURE_DECISIONS.md` (ADR-001: foundational docs change only for significant architectural reasons, not routine feature work). Future sessions should not re-litigate these without flagging it explicitly as an architecture decision:

- **Layered architecture (target):** Presentation → Workflow → Skill → Knowledge → Service → Infrastructure → Storage. Internally agent-oriented; externally skill-oriented.
- **Workflows orchestrate, never implement business logic.** Skills solve exactly one business problem each and must remain independently reusable/testable, workflow-agnostic.
- **Knowledge stays external to Skills** via versioned Knowledge Packs — never hardcoded business rules.
- **AI never bypasses deterministic validation.** Every workflow should follow Rules → AI → Validation → Human Review.
- **Human Review is a first-class, any-stage capability** — not a final pipeline step.
- **LLM-agnostic:** no Skill should hard-depend on one AI provider.
- **PII must be detected and masked before anything reaches an LLM.**
- **No circular dependencies; vendor neutrality; fail gracefully** (non-critical Skill failure shouldn't kill a workflow).
- **C² Engineering Workflow** governs how work gets done (§7) — this is itself a stable, settled process, not just a suggestion.

---

## 3. Current Implementation State

This is the actual state of the code as of Wave 2 (implemented, pending commit), **not** the target state described in §2 or in `SKILLS_GUIDE.md`/`WORKFLOW_GUIDE.md`.

**What's real and wired end-to-end today:**
- PII masking (naive regex-based) → Requirement extraction/classification/validation/review/quality-scoring/readiness-critic (`requirement_engine/` + `critics/` + `services/readiness_service.py`) → **Governance Gate (new, Wave 2)** → UI Analysis, Impact Analysis, Testcase Generation, Critic agents (all pure LLM-prompt wrappers, no deterministic backing) → Traceability, Coverage, Evaluation, Metrics → Streamlit UI.
- **The Workflow Governance Layer is real and wired (Wave 2):** a new `governance/` package (`WorkflowStatus`, `GateDecision`, `RetryPolicy`, `ExecutionGuard`, `OutputValidator`, `GateEngine`, `WorkflowStep`) now enforces "Rules → AI → Validation → Human Review" in code. The Requirement Readiness Critic's verdict (`approved`/`confidence`/`needs_sme`) is translated into a `GateDecision` (`critics/requirement_readiness_critic.py::to_gate_decision`) and can halt the workflow before any AI stage runs — `WorkflowState.status` now genuinely reflects `RUNNING`/`PAUSED_FOR_REVIEW`/`NEEDS_SME`/`FAILED_VALIDATION`/`FAILED_AGENT`/`COMPLETED`, and the Streamlit UI renders accordingly instead of always claiming "Analysis Completed." Full detail: `docs/waves/WAVE_2.md`; design reasoning: `docs/ARCHITECTURE_DECISIONS.md` ADR-004.
- **Agent execution is now resilient, not fragile:** `ExecutionGuard` catches exceptions (with a narrow, caller-supplied transient-exception retry policy) instead of letting one agent failure crash the whole process; `ExecutionRecord.status`/`error_message` reflect true outcome instead of a hardcoded `"SUCCESS"`.
- **AI output is validated before it reaches workflow state:** `LLMAgent.validate_result()` (default: reject empty/falsy output) closes the previously-silent failure where `OpenAIService.extract_json()` returning `{}` on malformed JSON flowed downstream as if it were a legitimate result.
- The Requirement Readiness Skill (shipped `ee8e9e1`/`959ea54`) and Wave 1's cleanup/refactor/bug-fix work (shipped `dbaabf2`/`236259c`) are both live.
- **Config has a single source of truth:** `config/settings.py` is now actually imported by `services/openai_service.py` (previously duplicated via a second `os.getenv()` call).
- **PII masking reports accurate redaction counts** (previously a boolean pretending to be a count).
- **Dead/orphaned modules removed:** `storage/sqlite_store.py`, `models/schemas.py`, `services/requirement_service.py`, `agents/requirement_quality_agent.py`, `agents/requirement_review_agent.py`, `requirement_engine/constants.py`, `services/logger_service.py`.
- **`agents/base_agent.py` provides a shared `LLMAgent` base class**, used by `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, and `CriticAgent` — collapses what was four copies of identical constructor/build-prompt/call-LLM/store-result wiring.
- **Root-level scratch scripts now live in `scripts/dev/`** (`smoke_workflow.py`, `smoke_requirement_engine.py`, plus the moved `debug_*.py` files) — two were renamed to `smoke_*.py` specifically to avoid pytest auto-collecting live-API scripts with no assertions.
- **Documentation is now fully version-controlled.** All of `docs/` was uncommitted across recent sessions (see the now-resolved assumption below); everything is committed as of `3b84d25`. Engineering records now follow a two-layer convention: `docs/waves/WAVE_N.md` (one file per wave, written once, never rewritten) for the detailed point-in-time record, and `docs/LESSONS_LEARNED.md` for the curated, cross-wave CCAF/interview revision guide. See `docs/waves/README.md` for the template.

**What the target architecture describes but does not exist yet:**
- No `knowledge/` directory anywhere — all domain rules/taxonomies (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, reviewer keyword rules, every agent prompt) are hardcoded in Python.
- No `skills/` directory — Skill-shaped logic (Readiness orchestration, Traceability, Coverage) currently lives under `services/`, and `critics/` is an entire undocumented layer that `ARCHITECTURE.md` still doesn't name explicitly (though its `governance/` counterpart now is, per ADR-004).
- **Resume-after-pause is not implemented.** The Governance Gate can halt a run (Wave 2), but a paused `WorkflowState` is only returned to the caller within that single request — there is no persistence layer letting a human act on it later and have the workflow continue. This is the "allow execution to continue once resolved" half of `ARCHITECTURE.md`'s Human Review Architecture section, blocked on decision #9.
- No schema/deterministic validation of AI agent output *beyond* the minimal non-empty-result check added in Wave 2 (e.g., generated testcases' internal shape — titles, steps, expected results — is still trusted as-is once the top-level dict is non-empty).
- `test_design/` package exists (matches `SPRINT_3_DESIGN.md`'s intended module names) but **every file in it is an empty stub** — Scenario Analyzer, Duplicate Detector, Weak Test Detector, etc. are all unimplemented. Still uncommitted.
- Real automated test suite: 38 tests passing across `tests/` (17 from Wave 1, 21 new from Wave 2's governance layer). Root-level `debug_*.py` scripts (in `scripts/dev/`) still contain zero assertions; `tests/test_imports.py` still triggers a harmless pytest collection warning (unrelated to Wave 2, not yet fixed).

**Known correctness bug — RESOLVED (Wave 1):** `WorkflowState.critic_review` was a single field written by both the deterministic Requirement Readiness critic and the AI `CriticAgent`, so the AI run silently overwrote the rule-based verdict before it reached the UI. Fixed by replacing it with `critic_reviews: dict`, keyed by critic name. Full reasoning: `docs/ARCHITECTURE_DECISIONS.md` ADR-002.

**Known correctness gap — RESOLVED (Wave 2):** the deterministic readiness critic's verdict was computed but never consulted — every requirement flowed through every AI stage regardless of its confidence or SME-review flag. Fixed via the Governance Gate (`governance/gate_engine.py` + `critics/requirement_readiness_critic.py::to_gate_decision`); a rejected or SME-flagged requirement now halts before any further AI cost is spent. Full reasoning: `docs/ARCHITECTURE_DECISIONS.md` ADR-004.

**Known dead code:** `services/requirement_intelligence_service.py` remains as an open, undecided empty stub — deliberately not swept up with the rest, since its name implies unresolved intent rather than confirmed-dead scaffolding (needs Architect input on build vs. delete).

**Repo hygiene note:** `README.md`/`requirements.txt` corruption was fixed in Wave 1 (`dbaabf2`) — **and recurred twice during Wave 2's session** (unexplained text appended to `requirements.txt`, including one instance instructing concealment from the Product Owner). Cleaned both times; root cause still not identified. This is no longer a one-off — worth the Architect's/Giri's direct attention as a possible tooling/environment issue, independent of any wave's scope.

---

## 4. Current Sprint

`docs/SPRINT_3_DESIGN.md` describes the intended current sprint: **"Enterprise Test Design Skill v1.0"** — Scenario Analyzer → Testcase Generation → Coverage Analyzer → Quality Analyzer → Duplicate Detector → Weak Test Detector → Enterprise Test Design Critic. The `test_design/` package was scaffolded to match this design, but **contains zero implementation** — Sprint 3 has not actually started in code yet.

The most recent shipped work (commits `ee8e9e1`, `959ea54`) was the **Requirement Readiness Skill**, which is not the subject of `SPRINT_3_DESIGN.md`. This mismatch between the written sprint plan and the actual last-shipped feature is flagged in §Assumptions — it's unclear whether Requirement Readiness was unplanned interleaved work, an unlabeled "Sprint 2.5," or whether the sprint doc is stale.

---

## 5. Active Backlog (summary)

A full 24-item backlog was produced by an architecture audit prior to Wave 1. By category:

- **Immediate Bugs (4) — ALL RESOLVED (Wave 1):** critic-review overwrite bug (`236259c`); corrupted `requirements.txt` (`dbaabf2`); corrupted `README.md` (`dbaabf2`); PII service's fake "count" field (`dbaabf2`).
- **Refactoring (6) — ALL RESOLVED (Wave 1, `dbaabf2`):** collapse duplicated LLM-agent boilerplate; delete confirmed-dead files; consolidate OpenAI model config; clear root-level debug script clutter; normalize `services/__init__.py` exports; move a small UI business-decision out of `streamlit_app.py`.
- **Architecture Decisions Required (9):** see §6. Decision #2 resolved (Wave 2, halt half); decision #3's data-loss half resolved (Wave 1); 7 remain open.
- **Future Enhancements (3):** build a real pytest suite (started — `tests/test_critic_reviews.py`); improve PII detection robustness; resolve the intent of `requirement_intelligence_service.py`.
- **Documentation Improvements (2):** fix stale README architecture diagram; document `critics/` in `ARCHITECTURE.md`. Neither done yet.

Full descriptions/effort/priority live in this session's conversation history and should be migrated into `docs/PRODUCT_BACKLOG.md` (currently an empty placeholder) as a follow-up — not yet done.

---

## 6. Pending Architecture Decisions

These require Architect (ChatGPT) sign-off before implementation, per the C² workflow:

1. **Knowledge Pack mechanism** — format and loading strategy for externalizing hardcoded domain rules/prompts.
2. **Human-review/validation gate design** — **RESOLVED for the halt half (Wave 2):** the Governance Gate (`governance/gate_engine.py`, `governance/workflow_step.py`) halts a workflow when a Skill/Critic's `GateDecision` says to. Still open: the resume half — see decision #9.
3. **Reconciling the two independent "readiness" verdicts** (quality-score status vs. readiness-critic approval). **Data-loss half resolved (Wave 1)** — see ADR-002. **Working answer adopted for the UX half (Wave 2):** rather than merging verdicts, each producer's gate stands alone and the first to say "halt" wins — no reconciliation UI has been built, but the design no longer treats this as blocked on one. Revisit if two gates ever need to disagree about the *same* step.
4. **Where AI-output schema validation lives** before downstream Skills consume it. **Partially addressed (Wave 2):** a minimal, domain-neutral "non-empty result" check now runs in `LLMAgent.execute()` via `governance/output_validator.py`. Still open: per-field/shape validation of what a valid testcase, UI analysis, etc. actually contains.
5. **Fate of `test_design/`** — build it out as the real Skill layer, or delete the stubs and rethink Sprint 3's shape. Building it out is now lower-risk than before Wave 2, since it would inherit a working gate instead of repeating the ignored-verdict pattern.
6. **Relocating Skill-shaped logic out of `services/`** (Readiness, Traceability, Coverage orchestration).
7. **Formal directory-to-layer mapping** — introducing `skills/`/`knowledge/`, and deciding what `critics/` is. **Partially informed (Wave 2):** `governance/` was added as a new top-level package without waiting for this decision, justified as the concrete implementation of responsibilities `ARCHITECTURE.md`'s Workflow Layer already claimed ("approvals," "auditability") — see ADR-004 (C). This sets a precedent worth confirming: is "already-claimed-responsibility → new package is fine without this decision" the right test going forward?
8. **How `workflow.py` should model non-agent steps** (Traceability/Coverage/Evaluation/Metrics currently bypass the agent-loop pattern). Wave 2's `WorkflowStep`/`ExecutionGuard`/`GateEngine` pattern only wraps agent-loop steps — the post-loop deterministic services remain unwrapped and un-gated, same as before.
9. **Persistence strategy** — whether/what workflow runs should persist at all, now that SQLite integration is fully dead. **Now higher priority than before Wave 2:** resolving this unlocks true suspend/resume for a paused workflow, the remaining half of decision #2.
10. **(New, Wave 2) `critic_reviews`'s free-string keys** — Wave 1 flagged converting these to an enum as a "revisit when a third critic arrives" item; Wave 2's gate now reads `state.critic_reviews.get("requirement_readiness", {})` by that same string, arguably past the trigger point. Not yet converted.

---

## 7. Current C² Engineering Workflow

Architecture → ChatGPT → Implementation → Claude → Verification → ChatGPT → Documentation → Git Repository → Continuous Learning.

ChatGPT architects and verifies; Claude implements; the loop always closes through documentation before returning to architecture. This document's own update protocol (see top) is part of that Documentation step — implementation sessions propose, they don't unilaterally commit context changes.

---

## 8. Current Responsibilities

**ChatGPT (Architect):** architecture, product direction, workflow design, enterprise/design decisions, roadmap, engineering coaching, implementation verification.

**Claude (Implementation Engineer):** production-ready implementation of Skills/Workflows, refactoring, MCP/SDK/CLI tooling, reusable components — implements, does not architect. Flags architecture-shaped questions back rather than deciding them unilaterally (see §6).

**Giri (Human-in-the-loop, final decision-maker):** owns every final decision; approves architecture and backlog priority; the project's primary learner. Neither AI role should silently invent business requirements — when confidence is insufficient, the expected behavior is to ask/recommend/escalate, never fabricate.

---

## 9. Current Learning Objectives

Per `CLAUDE.md`'s Learning Philosophy, priority order is: **learn deeply → build production-quality software → leave the project better than yesterday.** Every significant implementation is expected to be traceable to:

- which engineering principle it applies (from `ENGINEERING_PRINCIPLES.md`),
- which Anthropic/Claude concept it exercises,
- relevance to ACE AI / Claude Certified Architect (CCAF) curriculum where applicable.

The long-term target roles are AI Engineer, Enterprise AI Architect, QA Architect, Automation Architect, and AI Product Engineer — architecture and documentation quality count as learning output, not just shipped code.

---

## Assumptions Made

Originally inferred from file state and git history, not confirmed by the Architect. Status updated 2026-07-07 — items 2 and 3 are now resolved; the rest remain open and should still be verified before this document is promoted to v1.0:

1. **Sprint numbering is unclear.** Still open. `SPRINT_3_DESIGN.md` describes a sprint that the last shipped feature (Requirement Readiness) isn't part of, and Wave 1 (this session) used "Wave" as its unit of work instead of "Sprint" — it's unverified whether these are the same tracking system, parallel systems, or whether Wave/Sprint terminology itself needs reconciling. Flagged, not resolved.
2. **RESOLVED (2026-07-07):** `ROADMAP.md`, `PRODUCT_BACKLOG.md`, `FIRST_DAY.md`, `KNOWLEDGE_PACKS.md`, `CODING_STANDARDS.md`, and `QA_AI_COPILOT_PHILOSOPHY.md` are committed as 0-byte placeholders — confirmed intentional (not yet written), now tracked in git rather than floating as an unverified working-tree state.
3. **RESOLVED (2026-07-07):** all of `docs/` is now committed (`3b84d25`) — confirmed as intentional work-in-progress documentation, not accidental staging. See `docs/ARCHITECTURE_DECISIONS.md` ADR-003 for the restructuring decision made alongside committing it.
4. **`critics/` was treated as real, in-production code** (not a stub), distinct from the still-unimplemented `test_design/` critic. Still unconfirmed as an intentional distinction — not addressed this session.
5. **I assumed the Requirement Readiness Skill is considered "done"/shipped** rather than still in progress, based on the commit message "Release ... v1.0" — still unverified against any actual Definition-of-Done checklist being run.
6. **I assumed `test_design/`'s empty stub files represent scaffolding-not-yet-filled**, rather than an abandoned/superseded direction — still open, materially affects whether Pending Decision #5 (§6) is "build it" vs. "delete it." `test_design/` remains uncommitted and untouched this session.
7. **I assumed the 24-item backlog is exhaustive enough to seed §5/§6** — still unverified against an Architect-level review; Wave 1 closed 10 of the 24 items but did not re-audit for completeness.
8. **The corrupted `README.md`/`requirements.txt` state was assumed to be accidental** — moot now (fixed in Wave 1), but the root cause was never confirmed with Giri, so the same class of corruption could recur unnoticed.

# QA AI Copilot — Master Context

**Version 0.2 — Updated with Giri's explicit approval, 2026-07-07.**
Last generated: 2026-07-07, from commit `3b84d25` (Wave 1 fully committed: `dbaabf2`, `236259c`, `3b84d25`).

This is the primary onboarding document for any new Claude session working on QA AI Copilot. Read this before reading any other doc in `docs/`. It exists because the other docs (`ARCHITECTURE.md`, `SKILLS_GUIDE.md`, `WORKFLOW_GUIDE.md`, etc.) describe the **target** design in detail but do not say how much of it is actually built, nor what's in flight right now. This document draws that line.

For a short, scannable "start here" pointer before reading the rest of this file, see `docs/SESSION_HANDOFF.md`.

---

## 0. Current Status (as of end of session, 2026-07-07)

- **Milestone:** Post-Phase-3 hardening — closing out the architecture-review backlog before Sprint 3 / Wave 2 begins.
- **Current wave:** **Wave 1 — Repository Cleanup, Agent Framework Improvements & Critic Data Contract Repair.** Status: **complete and committed** (`dbaabf2`, `236259c`, `3b84d25`). Full record: `docs/waves/WAVE_1.md`.
- **Next wave:** **Not yet defined.** No Wave 2 scope has been architected or approved. Per the C² workflow, that's the Architect's (ChatGPT's) call, not Claude's to assume — see §6 for the candidate queue this session pulled from the existing backlog, not a committed plan.
- **Next action:** Architect/Giri to prioritize one item from the Implementation Queue below (or the §6 pending-decision list) as Wave 2's scope.
- **Open decisions:** 9 pending architecture decisions from the original review (§6), one (`#3`) now partially resolved this wave — see `docs/ARCHITECTURE_DECISIONS.md` ADR-002.
- **Implementation queue (unordered, not yet prioritized):**
  1. Migrate the 24-item backlog into `docs/PRODUCT_BACKLOG.md` (currently empty).
  2. Resolve `services/requirement_intelligence_service.py`'s intent (build vs. delete).
  3. Decide the fate of `test_design/` (§6 decision #5) — Sprint 3 stubs, unimplemented.
  4. Any of the 9 pending architecture decisions in §6, at the Architect's discretion.

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

This is the actual state of the code as of `3b84d25` (Wave 1 complete), **not** the target state described in §2 or in `SKILLS_GUIDE.md`/`WORKFLOW_GUIDE.md`.

**What's real and wired end-to-end today:**
- PII masking (naive regex-based) → Requirement extraction/classification/validation/review/quality-scoring/readiness-critic (`requirement_engine/` + `critics/` + `services/readiness_service.py`) → UI Analysis, Impact Analysis, Testcase Generation, Critic agents (all pure LLM-prompt wrappers, no deterministic backing) → Traceability, Coverage, Evaluation, Metrics → Streamlit UI.
- The Requirement Readiness Skill (shipped `ee8e9e1`/`959ea54`) and Wave 1's cleanup/refactor/bug-fix work (shipped `dbaabf2`/`236259c`) are both live.
- **Config has a single source of truth:** `config/settings.py` is now actually imported by `services/openai_service.py` (previously duplicated via a second `os.getenv()` call).
- **PII masking reports accurate redaction counts** (previously a boolean pretending to be a count).
- **Dead/orphaned modules removed:** `storage/sqlite_store.py`, `models/schemas.py`, `services/requirement_service.py`, `agents/requirement_quality_agent.py`, `agents/requirement_review_agent.py`, `requirement_engine/constants.py`, `services/logger_service.py`.
- **`agents/base_agent.py` provides a shared `LLMAgent` base class**, used by `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, and `CriticAgent` — collapses what was four copies of identical constructor/build-prompt/call-LLM/store-result wiring.
- **Root-level scratch scripts now live in `scripts/dev/`** (`smoke_workflow.py`, `smoke_requirement_engine.py`, plus the moved `debug_*.py` files) — two were renamed to `smoke_*.py` specifically to avoid pytest auto-collecting live-API scripts with no assertions.
- **Documentation is now fully version-controlled.** All of `docs/` was uncommitted across recent sessions (see the now-resolved assumption below); everything is committed as of `3b84d25`. Engineering records now follow a two-layer convention: `docs/waves/WAVE_N.md` (one file per wave, written once, never rewritten) for the detailed point-in-time record, and `docs/LESSONS_LEARNED.md` for the curated, cross-wave CCAF/interview revision guide. See `docs/waves/README.md` for the template.

**What the target architecture describes but does not exist yet:**
- No `knowledge/` directory anywhere — all domain rules/taxonomies (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, reviewer keyword rules, every agent prompt) are hardcoded in Python.
- No `skills/` directory — Skill-shaped logic (Readiness orchestration, Traceability, Coverage) currently lives under `services/`, and `critics/` is an entire undocumented layer not mentioned in `ARCHITECTURE.md` at all.
- No enforced validation/human-review gate: both the deterministic readiness critic and the AI critic compute a verdict, and (as of this wave) both verdicts now reliably reach `WorkflowState.critic_reviews` without overwriting each other — but nothing in `workflows/workflow.py` yet checks either one to pause or stop execution. That gate itself is still unbuilt (§6 decision #2).
- No schema/deterministic validation of AI agent output before it flows downstream (e.g., generated testcases are trusted as-is).
- `test_design/` package exists (matches `SPRINT_3_DESIGN.md`'s intended module names) but **every file in it is an empty stub** — Scenario Analyzer, Duplicate Detector, Weak Test Detector, etc. are all unimplemented. Deliberately left uncommitted this session (unrelated to the docs checkpoint).
- Real automated test suite is just starting: `tests/test_critic_reviews.py` is the first real pytest test with actual assertions (Wave 1). Root-level `debug_*.py` scripts (now in `scripts/dev/`) still contain zero assertions.

**Known correctness bug — RESOLVED this wave:** `WorkflowState.critic_review` was a single field written by both the deterministic Requirement Readiness critic and the AI `CriticAgent`, so the AI run silently overwrote the rule-based verdict before it reached the UI. Fixed by replacing it with `critic_reviews: dict`, keyed by critic name (`"requirement_readiness"`, `"testcase"`), covered by `tests/test_critic_reviews.py`. This resolves the *data-loss* half of pending decision #3 (§6); the *reconciliation/UX* half (how a reviewer should read two verdicts together) is still open. Full reasoning: `docs/ARCHITECTURE_DECISIONS.md` ADR-002.

**Known dead code:** `services/requirement_intelligence_service.py` remains as an open, undecided empty stub — deliberately not swept up with the rest, since its name implies unresolved intent rather than confirmed-dead scaffolding (needs Architect input on build vs. delete).

**Repo hygiene note:** resolved this session — all of `docs/` is now committed (`3b84d25`). `README.md` and `requirements.txt` corruption was fixed in Wave 1 (`dbaabf2`).

---

## 4. Current Sprint

`docs/SPRINT_3_DESIGN.md` describes the intended current sprint: **"Enterprise Test Design Skill v1.0"** — Scenario Analyzer → Testcase Generation → Coverage Analyzer → Quality Analyzer → Duplicate Detector → Weak Test Detector → Enterprise Test Design Critic. The `test_design/` package was scaffolded to match this design, but **contains zero implementation** — Sprint 3 has not actually started in code yet.

The most recent shipped work (commits `ee8e9e1`, `959ea54`) was the **Requirement Readiness Skill**, which is not the subject of `SPRINT_3_DESIGN.md`. This mismatch between the written sprint plan and the actual last-shipped feature is flagged in §Assumptions — it's unclear whether Requirement Readiness was unplanned interleaved work, an unlabeled "Sprint 2.5," or whether the sprint doc is stale.

---

## 5. Active Backlog (summary)

A full 24-item backlog was produced by an architecture audit prior to Wave 1. By category:

- **Immediate Bugs (4) — ALL RESOLVED (Wave 1):** critic-review overwrite bug (`236259c`); corrupted `requirements.txt` (`dbaabf2`); corrupted `README.md` (`dbaabf2`); PII service's fake "count" field (`dbaabf2`).
- **Refactoring (6) — ALL RESOLVED (Wave 1, `dbaabf2`):** collapse duplicated LLM-agent boilerplate; delete confirmed-dead files; consolidate OpenAI model config; clear root-level debug script clutter; normalize `services/__init__.py` exports; move a small UI business-decision out of `streamlit_app.py`.
- **Architecture Decisions Required (9):** see §6. Decision #3 partially resolved this wave (data-loss half only).
- **Future Enhancements (3):** build a real pytest suite (started — `tests/test_critic_reviews.py`); improve PII detection robustness; resolve the intent of `requirement_intelligence_service.py`.
- **Documentation Improvements (2):** fix stale README architecture diagram; document `critics/` in `ARCHITECTURE.md`. Neither done yet.

Full descriptions/effort/priority live in this session's conversation history and should be migrated into `docs/PRODUCT_BACKLOG.md` (currently an empty placeholder) as a follow-up — not yet done.

---

## 6. Pending Architecture Decisions

These require Architect (ChatGPT) sign-off before implementation, per the C² workflow:

1. **Knowledge Pack mechanism** — format and loading strategy for externalizing hardcoded domain rules/prompts.
2. **Human-review/validation gate design** — how workflows actually pause on low-confidence or failed-critic results.
3. **Reconciling the two independent "readiness" verdicts** (quality-score status vs. readiness-critic approval). **Partially resolved (Wave 1):** the data-loss bug (one verdict silently overwriting the other) is fixed — see `ARCHITECTURE_DECISIONS.md` ADR-002. Still open: how a reviewer should read/reconcile two coexisting verdicts in the UI/UX.
4. **Where AI-output schema validation lives** before downstream Skills consume it.
5. **Fate of `test_design/`** — build it out as the real Skill layer, or delete the stubs and rethink Sprint 3's shape.
6. **Relocating Skill-shaped logic out of `services/`** (Readiness, Traceability, Coverage orchestration).
7. **Formal directory-to-layer mapping** — introducing `skills/`/`knowledge/`, and deciding what `critics/` is.
8. **How `workflow.py` should model non-agent steps** (Traceability/Coverage/Evaluation/Metrics currently bypass the agent-loop pattern).
9. **Persistence strategy** — whether/what workflow runs should persist at all, now that SQLite integration is fully dead.

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

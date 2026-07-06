# QA AI Copilot — Master Context

**Version 0.1 — Draft, not yet Architect-approved.**
Last generated: 2026-07-05, from commit `959ea54` plus uncommitted working-tree state.

This is the primary onboarding document for any new Claude session working on QA AI Copilot. Read this before reading any other doc in `docs/`. It exists because the other docs (`ARCHITECTURE.md`, `SKILLS_GUIDE.md`, `WORKFLOW_GUIDE.md`, etc.) describe the **target** design in detail but do not say how much of it is actually built, nor what's in flight right now. This document draws that line.

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

This is the actual state of the code as of `959ea54` + uncommitted changes, **not** the target state described in §2 or in `SKILLS_GUIDE.md`/`WORKFLOW_GUIDE.md`. A full architecture audit was completed this session; only the highlights are captured here.

**What's real and wired end-to-end today:**
- PII masking (naive regex-based) → Requirement extraction/classification/validation/review/quality-scoring/readiness-critic (`requirement_engine/` + `critics/` + `services/readiness_service.py`) → UI Analysis, Impact Analysis, Testcase Generation, Critic agents (all pure LLM-prompt wrappers, no deterministic backing) → Traceability, Coverage, Evaluation, Metrics → Streamlit UI.
- The Requirement Readiness Skill (shipped in the last two commits) is the newest working capability.

**What the target architecture describes but does not exist yet:**
- No `knowledge/` directory anywhere — all domain rules/taxonomies (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, reviewer keyword rules, every agent prompt) are hardcoded in Python.
- No `skills/` directory — Skill-shaped logic (Readiness orchestration, Traceability, Coverage) currently lives under `services/`, and `critics/` is an entire undocumented layer not mentioned in `ARCHITECTURE.md` at all.
- No enforced validation/human-review gate: both the deterministic readiness critic and the AI critic compute a verdict, but nothing in `workflows/workflow.py` ever checks either one to pause or stop execution.
- No schema/deterministic validation of AI agent output before it flows downstream (e.g., generated testcases are trusted as-is).
- `test_design/` package exists (matches `SPRINT_3_DESIGN.md`'s intended module names) but **every file in it is an empty stub** — Scenario Analyzer, Duplicate Detector, Weak Test Detector, etc. are all unimplemented.
- No real automated test suite — `tests/` and root-level `debug_*.py`/`test_*.py` scripts contain zero assertions.

**Known correctness bug:** `WorkflowState.critic_review` is written by the deterministic Requirement Readiness critic and then silently overwritten by the AI `CriticAgent` later in the same run — the rule-based verdict never reaches the UI.

**Known dead code:** `storage/sqlite_store.py` (orphaned since the `copilot.db` removal commit), `config/settings.py` (never imported — `openai_service.py` duplicates its constant instead), `models/schemas.py`, `services/requirement_service.py`, and several empty stub agent/service files.

**Repo hygiene note:** every file in `docs/` is currently **untracked** (never committed) — this includes this document. `README.md` and `requirements.txt` currently have uncommitted corruption (stray pasted text and a leaked `git rebase --continue`) that predates this session and has not been fixed yet.

---

## 4. Current Sprint

`docs/SPRINT_3_DESIGN.md` describes the intended current sprint: **"Enterprise Test Design Skill v1.0"** — Scenario Analyzer → Testcase Generation → Coverage Analyzer → Quality Analyzer → Duplicate Detector → Weak Test Detector → Enterprise Test Design Critic. The `test_design/` package was scaffolded to match this design, but **contains zero implementation** — Sprint 3 has not actually started in code yet.

The most recent shipped work (commits `ee8e9e1`, `959ea54`) was the **Requirement Readiness Skill**, which is not the subject of `SPRINT_3_DESIGN.md`. This mismatch between the written sprint plan and the actual last-shipped feature is flagged in §Assumptions — it's unclear whether Requirement Readiness was unplanned interleaved work, an unlabeled "Sprint 2.5," or whether the sprint doc is stale.

---

## 5. Active Backlog (summary)

A full 24-item backlog was produced this session by auditing the code against §2/§3's gap. None of it is approved or started. By category:

- **Immediate Bugs (4):** critic-review overwrite bug; corrupted `requirements.txt`; corrupted `README.md`; PII service's fake "count" field.
- **Refactoring (6):** collapse duplicated LLM-agent boilerplate; delete confirmed-dead files; consolidate OpenAI model config; clear root-level debug script clutter; normalize `services/__init__.py` exports; move a small UI business-decision out of `streamlit_app.py`.
- **Architecture Decisions Required (9):** see §6.
- **Future Enhancements (3):** build a real pytest suite; improve PII detection robustness; resolve the intent of `requirement_intelligence_service.py`.
- **Documentation Improvements (2):** fix stale README architecture diagram; document `critics/` in `ARCHITECTURE.md`.

Full descriptions/effort/priority live in this session's conversation history and should be migrated into `docs/PRODUCT_BACKLOG.md` (currently an empty placeholder) as a follow-up — not yet done.

---

## 6. Pending Architecture Decisions

These require Architect (ChatGPT) sign-off before implementation, per the C² workflow:

1. **Knowledge Pack mechanism** — format and loading strategy for externalizing hardcoded domain rules/prompts.
2. **Human-review/validation gate design** — how workflows actually pause on low-confidence or failed-critic results.
3. **Reconciling the two independent "readiness" verdicts** (quality-score status vs. readiness-critic approval).
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

Everything below was inferred from the current file state and git history, not confirmed by the Architect. Verify before this document is promoted to v1.0:

1. **Sprint numbering is unclear.** I assumed `SPRINT_3_DESIGN.md` describes the *current* sprint, but the last shipped feature (Requirement Readiness) isn't part of that design doc's scope. It's unverified whether Requirement Readiness was an unplanned/interleaved sprint, or whether sprint numbering/tracking exists anywhere authoritative.
2. **`ROADMAP.md`, `PRODUCT_BACKLOG.md`, `FIRST_DAY.md`, `KNOWLEDGE_PACKS.md`, `CODING_STANDARDS.md`, and `QA_AI_COPILOT_PHILOSOPHY.md` are all 0-byte placeholders.** I've treated them as "not yet written" rather than "intentionally empty" — unverified which.
3. **All of `docs/` is uncommitted (git status shows `??` for every file).** I assumed this reflects work-in-progress documentation authored across recent sessions, not accidental staging — unverified.
4. **`critics/` was treated as real, in-production code** (not a stub), distinct from the still-unimplemented `test_design/` critic. Confirm this distinction is intentional.
5. **I assumed the Requirement Readiness Skill (last commit) is considered "done"/shipped** rather than still in progress, based on the commit message "Release ... v1.0" — unverified against any actual Definition-of-Done checklist being run.
6. **I assumed `test_design/`'s empty stub files represent scaffolding-not-yet-filled**, rather than an abandoned/superseded direction — this materially affects whether Pending Decision #5 (§6) is "build it" vs. "delete it."
7. **I assumed the backlog produced this session is exhaustive enough to seed §5/§6**, but it came from one audit pass and may have missed items an Architect-level review would catch.
8. **The corrupted `README.md`/`requirements.txt` state was assumed to be accidental** (paste/rebase mishap) rather than a deliberate in-progress edit — unverified with Giri.

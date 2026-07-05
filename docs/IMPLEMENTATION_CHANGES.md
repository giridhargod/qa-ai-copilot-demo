# Implementation Changes — Execution Phase (Wave 1)

Status: **Implemented, not committed.** Awaiting review and approval.

Scope: the approved Immediate Bugs and Refactoring items from the architecture review backlog. No architecture-decision items were implemented (Knowledge Packs, Human Review Gate, Readiness redesign, AI output validation, Skill layer migration, directory restructuring, workflow redesign, persistence redesign) — see §6 for how those surfaced during this work.

---

## 1. Files Changed

**Immediate Bugs**
- `requirements.txt` — removed corrupted trailing text.
- `README.md` — removed duplicated title block and leaked shell command; restored markdown structure (headers/bullets) that had been stripped in an earlier commit.
- `services/pii_service.py` — count logic rewritten.
- `config/settings.py` (unchanged, now actually consulted) / `services/openai_service.py` — config consolidation.

**Refactoring**
- Deleted: `agents/requirement_quality_agent.py`, `agents/requirement_review_agent.py`, `services/requirement_service.py`, `storage/sqlite_store.py` (and the now-empty `storage/` directory), `models/schemas.py`, `requirement_engine/constants.py`, `services/logger_service.py`.
- Moved: `debug_evaluation.py`, `debug_metrics.py`, `debug_traceability.py`, `temp_test.py` → `scripts/dev/`; `test_requirement_engine.py` → `scripts/dev/smoke_requirement_engine.py`; `test_workflow.py` → `scripts/dev/smoke_workflow.py`.
- `services/__init__.py` — export surface normalized.
- `services/file_service.py` — new `resolve_input()`.
- `app/streamlit_app.py` — input-precedence branch replaced with a call to `resolve_input()`.
- `agents/base_agent.py` — new `LLMAgent` base class.
- `agents/ui_agent.py`, `agents/impact_agent.py`, `agents/testcase_agent.py`, `agents/critic_agent.py` — rewritten on top of `LLMAgent`.

New doc: `docs/MASTER_CONTEXT.md` was already created in the prior session (not part of this wave); `docs/IMPLEMENTATION_CHANGES.md` is new, as explicitly required by this task.

---

## 2. Why Each File Changed

- **`requirements.txt`**: a stray line (`Would an Enterprise QA Lead actually use this?`, apparently pasted from `docs/CLAUDE.md`) had been appended to the dependency manifest. Confirmed via `git show HEAD` that the committed version was clean and only the working tree was corrupted. Restored to the clean, committed 8-line list.
- **`README.md`**: `git show HEAD:README.md` proved the duplicated title block (`QA AI Copilot / Overview / //README.md / QA AI Copilot / Overview`) and complete absence of markdown syntax was **already committed**, not just a working-tree artifact — it happened between the `70adbe7`/`87c5340` commits (which had proper `#`/`*` markdown) and `bc777a7`. The working tree additionally had `git rebase --continue` leaked onto the final line. Fixed both: removed the duplicate header, restored heading/bullet structure matching the last known-good formatted version, dropped the leaked command. Content/wording was preserved as-is — no new sections were added (e.g., the Requirement Readiness pipeline is still missing from the architecture diagram; that's a separate Documentation Improvement item, not in this wave's approved scope).
- **`services/pii_service.py`**: `count` was `1 if masked != user_input else 0` — a boolean pretending to be a count. Switched `re.sub` → `re.subn` for each masker and summed the four match counts, so `count` now reflects the actual number of redactions.
- **`config/settings.py` / `services/openai_service.py`**: `config/settings.py` defined `OPENAI_MODEL`/`OPENAI_API_KEY` but was never imported anywhere; `openai_service.py` independently called `load_dotenv()` + `os.getenv(...)` and hardcoded `"gpt-4o-mini"` a second time. `openai_service.py` now imports both constants from `config.settings`, which is the single source of truth. Verified `svc.model == OPENAI_MODEL` at runtime.
- **Deleted dead files**: each was confirmed via repo-wide grep to have zero importers/references anywhere outside itself before deletion (empty stub agents never wired into `agents/__init__.py`; `RequirementService` duplicated `RequirementExtractor` and was never imported; `sqlite_store.py` was orphaned since the `copilot.db` removal commit; `models/schemas.py`'s `TestCase` schema didn't even match real agent output shape; `requirement_engine/constants.py` and `services/logger_service.py` were empty). `services/requirement_intelligence_service.py` was deliberately **left alone** — unlike the others, its name suggests an intended future capability rather than confirmed-dead scaffolding, and resolving its intent was flagged as needing Architect input, not blanket cleanup.
- **Moved scratch scripts**: none were obsolete (all still run against current code), so per the instruction ("remove if obsolete") they were relocated rather than deleted. `test_requirement_engine.py`/`test_workflow.py` were also renamed to `smoke_*.py` — their `test_` prefix would make pytest auto-collect and execute them (they have no assertions, and executing them makes live OpenAI calls), which is unsafe once a real test suite exists. Added a repo-root `sys.path` bootstrap (mirroring `app/streamlit_app.py`'s existing pattern) to each so their absolute imports keep resolving from the new location.
- **`services/__init__.py`**: only re-exported 3 of 8 public service modules; everything else was imported via direct submodule paths. Now exports all eight public names so `services` has one consistent public API surface. (Existing call sites, e.g. in `workflows/workflow.py`, were left on their current submodule imports — changing those touches `workflow.py`'s deferred-import pattern, which is tied to pending architecture decision #8 and was left untouched.)
- **`app/streamlit_app.py` / `services/file_service.py`**: the file-vs-text input precedence decision was a small business rule embedded in the Presentation layer. Moved into `file_service.resolve_input()`; the view now just calls it. Behavior is identical (uploaded file still wins over typed text).
- **`agents/base_agent.py` + 4 agent files**: `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, `CriticAgent` were four copies of the same constructor → build-prompt → call-LLM → store-on-state wiring. Added `LLMAgent(BaseAgent)` owning that wiring; each subclass now only declares `name`, `prompt_template`, `get_input()`, and `store_result()`. Verified byte-for-byte identical prompt strings and state field writes via a scripted comparison against the original f-string templates (see §6), and re-ran the full workflow end-to-end successfully.

---

## 3. Engineering Principles Applied

- **#5 Modular Architecture / #15 Continuous Refactoring** (`ENGINEERING_PRINCIPLES.md`) — collapsing the 4x duplicated agent boilerplate into `LLMAgent`.
- **#10 Maintainability Over Cleverness** — the `LLMAgent` base stays a plain template method, no metaprogramming, matching the codebase's existing simplicity.
- **#6 Knowledge Separation / #5 Modular Architecture** — moving the input-precedence decision out of the Presentation layer into the Service layer.
- **#16 Document Important Decisions** — this document itself.
- **"Measure Before Improving"** — every deletion was verified dead via grep before removal, not assumed.

---

## 4. Architecture Principles Applied

- **"Presentation components should never contain business logic"** (`ARCHITECTURE.md`) — addressed via the `resolve_input()` move.
- **"Services provide reusable infrastructure... services should remain generic"** — the export-surface fix makes the Service layer's public API coherent (though the deeper issue — Skill-shaped logic living in `services/` — is untouched, per scope).
- **"Responsibilities should remain clearly separated"** — dead/orphaned modules removed so the directory tree reflects what's actually wired, not aspirational or abandoned code.
- Config consolidation follows the general "single source of truth" constraint implicit in avoiding vendor/config drift, even though it isn't named verbatim in `ARCHITECTURE.md`.

---

## 5. Relevant Anthropic / CCAF Concepts

- **Behavior-preserving refactoring under verification**: the `LLMAgent` extraction is a textbook case for demonstrating that an agent abstraction can be refactored without changing observable behavior — verified here by comparing generated prompts character-for-character before/after, not just by inspection. This is directly relevant to designing reliable multi-agent systems (a recurring CCAF theme): shared harnesses reduce the surface area where individual agents can silently drift from each other.
- **Tool/agent contract minimalism**: `LLMAgent`'s subclass contract (`prompt_template`, `get_input`, `store_result`) is intentionally the smallest interface that captures what varies between agents — mirrors the general principle of keeping agent/tool definitions narrow and single-purpose rather than over-parameterized.

---

## 6. Trade-offs

- **`README.md` reformatting** went slightly beyond literal "remove the corrupted lines" — it restored full markdown structure, since the file had zero markdown syntax and was unreadable as rendered output. This was judged to be squarely "fixing corruption" (format was demonstrably lost, per git history showing earlier commits had it) rather than a content redesign; no wording or sections were added/changed beyond that.
- **`services/__init__.py` export normalization was not propagated to call sites.** `workflows/workflow.py` and `agents/requirement_readiness_agent.py` still import services via direct submodule paths. Updating them would touch `workflow.py`'s existing deferred-import structure, which is explicitly tied to pending architecture decision #8 ("how workflow.py should model non-agent steps") — left alone to avoid pre-empting that decision.
- **`services/requirement_intelligence_service.py`** was left in place despite being an empty, unreferenced file, because it wasn't part of the "confirmed dead code" set (its name implies unresolved intent, not confirmed dead scaffolding) — deliberately not swept up with the rest.
- **The `critic_review` overwrite bug** (deterministic Readiness critic silently replaced by the AI `CriticAgent` in `WorkflowState`) was **not fixed** in this wave, even though it's a correctness bug, because the fix requires deciding how the two critic outputs should coexist in `WorkflowState` — that's pending architecture decision #3/#13, explicitly out of scope ("Readiness redesign," "Human Review Gate"). Flagging it again here rather than fixing it silently.
- Moving the scratch scripts to `scripts/dev/` plus renaming two of them is a slightly larger touch than a pure "move," but was necessary to actually achieve the goal (keeping them runnable, and preventing pytest from silently executing live-API scripts once `tests/` grows) rather than just relocating a problem.

---

## 7. Future Improvements

(Unchanged from the existing backlog — not re-litigated here.) Most relevant near-term follow-ups given this wave's work:
- Migrate the full 24-item backlog into `docs/PRODUCT_BACKLOG.md` (currently empty).
- Build a real pytest suite in `tests/` now that `scripts/dev/` is clearly separated from anything pytest should collect.
- Resolve `services/requirement_intelligence_service.py`'s intent (build vs. delete).
- All 9 pending architecture decisions from the prior review remain open and unaffected by this wave.

---

## 8. Proposed `MASTER_CONTEXT.md` Updates

Per this session's rule, `MASTER_CONTEXT.md` was **not** edited directly. Proposed changes below, pending approval:

**Added**
- A line under §3 (Current Implementation State) noting that config now has a single source of truth (`config/settings.py`), PII masking reports accurate counts, and dead/orphaned modules (`sqlite_store.py`, `models/schemas.py`, `services/requirement_service.py`, empty stub agents, `requirement_engine/constants.py`, `services/logger_service.py`) have been removed.
- A note that `agents/base_agent.py` now provides a shared `LLMAgent` base class used by `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, and `CriticAgent`.
- A note that root-level scratch scripts now live in `scripts/dev/` (two renamed to `smoke_*.py` to avoid pytest auto-collection).

**Changed**
- §3's "Known dead code" list should be updated to remove the now-deleted items and add a note that `services/requirement_intelligence_service.py` remains as an open, undecided stub (not swept up).
- §5 (Active Backlog) Refactoring category: mark the 6 refactoring items and the `openai_service.py`/`config/settings.py` consolidation and PII-count bug as done.

**Removed**
- The 4 "Immediate Bug" backlog entries for `requirements.txt`, `README.md`, PII count, and OpenAI config — resolved.
- The dead-code refactoring entry — resolved (with the `requirement_intelligence_service.py` carve-out noted above).

**Why the change is required**: `MASTER_CONTEXT.md` §3/§5 currently describe a pre-Wave-1 snapshot; leaving it unedited after this session would make it actively misleading for the next Claude session (it would re-flag already-fixed bugs and already-deleted files as open work).

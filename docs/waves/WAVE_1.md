# Wave 1 — Repository Cleanup and Agent Framework Improvements

Status: **Implemented and committed** (`dbaabf2`, `236259c`). Approved 2026-07-07.

See `docs/waves/README.md` for what this file is and what each section means.

---

## 1. Scope

The approved Immediate Bugs and Refactoring items from the architecture review backlog, plus one bug fix (`critic_review` overwrite, §4/§9) closed out after initial approval. No architecture-decision items were implemented (Knowledge Packs, Human Review Gate, Readiness redesign, AI output validation, Skill layer migration, directory restructuring, workflow redesign, persistence redesign) — see §8 for how those surfaced during this work.

---

## 2. Files Changed

**Immediate Bugs**
- `requirements.txt` — removed corrupted trailing text.
- `README.md` — removed duplicated title block and leaked shell command; restored markdown structure (headers/bullets) that had been stripped in an earlier commit.
- `services/pii_service.py` — count logic rewritten.
- `config/settings.py` (unchanged, now actually consulted) / `services/openai_service.py` — config consolidation.
- `models/workflow_state.py`, `agents/critic_agent.py`, `agents/requirement_readiness_agent.py`, `app/streamlit_app.py`, `scripts/dev/smoke_workflow.py` — `critic_review` → `critic_reviews` dict fix (see §4, §9). New: `tests/test_critic_reviews.py`.

**Refactoring**
- Deleted: `agents/requirement_quality_agent.py`, `agents/requirement_review_agent.py`, `services/requirement_service.py`, `storage/sqlite_store.py` (and the now-empty `storage/` directory), `models/schemas.py`, `requirement_engine/constants.py`, `services/logger_service.py`.
- Moved: `debug_evaluation.py`, `debug_metrics.py`, `debug_traceability.py`, `temp_test.py` → `scripts/dev/`; `test_requirement_engine.py` → `scripts/dev/smoke_requirement_engine.py`; `test_workflow.py` → `scripts/dev/smoke_workflow.py`.
- `services/__init__.py` — export surface normalized.
- `services/file_service.py` — new `resolve_input()`.
- `app/streamlit_app.py` — input-precedence branch replaced with a call to `resolve_input()`.
- `agents/base_agent.py` — new `LLMAgent` base class.
- `agents/ui_agent.py`, `agents/impact_agent.py`, `agents/testcase_agent.py`, `agents/critic_agent.py` — rewritten on top of `LLMAgent`.

New docs: `docs/MASTER_CONTEXT.md` was already created in a prior session (not part of this wave); `docs/waves/WAVE_1.md` (originally `docs/IMPLEMENTATION_CHANGES.md`) is new, as explicitly required by this task.

---

## 3. Business Problem Solved

The codebase had accumulated dead files, duplicated agent boilerplate, a corrupted manifest/README, and a silent data-loss bug (a QA verdict disappearing before reaching the reviewer) — all of which erode trust in the platform's output before it ever reaches an enterprise QA Lead. This wave removes that class of "the tool is quietly wrong or unmaintainable" risk without touching product behavior, so future feature work (Knowledge Packs, Human Review Gate, etc.) is built on a codebase that says what it does.

---

## 4. Why Each File Changed

- **`requirements.txt`**: a stray line (`Would an Enterprise QA Lead actually use this?`, apparently pasted from `docs/CLAUDE.md`) had been appended to the dependency manifest. Confirmed via `git show HEAD` that the committed version was clean and only the working tree was corrupted. Restored to the clean, committed 8-line list.
- **`README.md`**: `git show HEAD:README.md` proved the duplicated title block (`QA AI Copilot / Overview / //README.md / QA AI Copilot / Overview`) and complete absence of markdown syntax was **already committed**, not just a working-tree artifact — it happened between the `70adbe7`/`87c5340` commits (which had proper `#`/`*` markdown) and `bc777a7`. The working tree additionally had `git rebase --continue` leaked onto the final line. Fixed both: removed the duplicate header, restored heading/bullet structure matching the last known-good formatted version, dropped the leaked command. Content/wording was preserved as-is — no new sections were added (e.g., the Requirement Readiness pipeline is still missing from the architecture diagram; that's a separate Documentation Improvement item, not in this wave's approved scope).
- **`services/pii_service.py`**: `count` was `1 if masked != user_input else 0` — a boolean pretending to be a count. Switched `re.sub` → `re.subn` for each masker and summed the four match counts, so `count` now reflects the actual number of redactions.
- **`config/settings.py` / `services/openai_service.py`**: `config/settings.py` defined `OPENAI_MODEL`/`OPENAI_API_KEY` but was never imported anywhere; `openai_service.py` independently called `load_dotenv()` + `os.getenv(...)` and hardcoded `"gpt-4o-mini"` a second time. `openai_service.py` now imports both constants from `config.settings`, which is the single source of truth. Verified `svc.model == OPENAI_MODEL` at runtime.
- **Deleted dead files**: each was confirmed via repo-wide grep to have zero importers/references anywhere outside itself before deletion (empty stub agents never wired into `agents/__init__.py`; `RequirementService` duplicated `RequirementExtractor` and was never imported; `sqlite_store.py` was orphaned since the `copilot.db` removal commit; `models/schemas.py`'s `TestCase` schema didn't even match real agent output shape; `requirement_engine/constants.py` and `services/logger_service.py` were empty). `services/requirement_intelligence_service.py` was deliberately **left alone** — unlike the others, its name suggests an intended future capability rather than confirmed-dead scaffolding, and resolving its intent was flagged as needing Architect input, not blanket cleanup.
- **Moved scratch scripts**: none were obsolete (all still run against current code), so per the instruction ("remove if obsolete") they were relocated rather than deleted. `test_requirement_engine.py`/`test_workflow.py` were also renamed to `smoke_*.py` — their `test_` prefix would make pytest auto-collect and execute them (they have no assertions, and executing them makes live OpenAI calls), which is unsafe once a real test suite exists. Added a repo-root `sys.path` bootstrap (mirroring `app/streamlit_app.py`'s existing pattern) to each so their absolute imports keep resolving from the new location.
- **`services/__init__.py`**: only re-exported 3 of 8 public service modules; everything else was imported via direct submodule paths. Now exports all eight public names so `services` has one consistent public API surface. (Existing call sites, e.g. in `workflows/workflow.py`, were left on their current submodule imports — changing those touches `workflow.py`'s deferred-import pattern, which is tied to pending architecture decision #8 and was left untouched.)
- **`app/streamlit_app.py` / `services/file_service.py`**: the file-vs-text input precedence decision was a small business rule embedded in the Presentation layer. Moved into `file_service.resolve_input()`; the view now just calls it. Behavior is identical (uploaded file still wins over typed text).
- **`agents/base_agent.py` + 4 agent files**: `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, `CriticAgent` were four copies of the same constructor → build-prompt → call-LLM → store-on-state wiring. Added `LLMAgent(BaseAgent)` owning that wiring; each subclass now only declares `name`, `prompt_template`, `get_input()`, and `store_result()`. Verified byte-for-byte identical prompt strings and state field writes via a scripted comparison against the original f-string templates, and re-ran the full workflow end-to-end successfully.
- **`critic_review` → `critic_reviews` (dict)**: `WorkflowState.critic_review` was a single field written by both the deterministic Requirement Readiness critic and the AI `CriticAgent` — whichever ran second silently erased the other's verdict before it reached the UI. Originally deferred pending an architecture decision on how the two verdicts should coexist (§8, decision #3); resolved this wave with the minimal fix — a dict keyed by critic name (`"requirement_readiness"`, `"testcase"`) — rather than waiting on the larger reconciliation-UX decision, since the two verdicts don't need to be merged to stop overwriting each other.

---

## 5. Engineering Principles Applied

- **#5 Modular Architecture / #15 Continuous Refactoring** (`ENGINEERING_PRINCIPLES.md`) — collapsing the 4x duplicated agent boilerplate into `LLMAgent`.
- **#10 Maintainability Over Cleverness** — the `LLMAgent` base stays a plain template method, no metaprogramming, matching the codebase's existing simplicity.
- **#6 Knowledge Separation / #5 Modular Architecture** — moving the input-precedence decision out of the Presentation layer into the Service layer.
- **#13 Measure Quality** — the `critic_reviews` fix ships with a pytest assertion (`len(critic_reviews) == 2`) rather than a manual eyeball check, so the bug can't silently regress.
- **#16 Document Important Decisions** — this document itself.
- **"Measure Before Improving"** — every deletion was verified dead via grep before removal, not assumed.

---

## 6. Architecture Principles Applied

- **"Presentation components should never contain business logic"** (`ARCHITECTURE.md`) — addressed via the `resolve_input()` move.
- **"Services provide reusable infrastructure... services should remain generic"** — the export-surface fix makes the Service layer's public API coherent (though the deeper issue — Skill-shaped logic living in `services/` — is untouched, per scope).
- **"Responsibilities should remain clearly separated"** — dead/orphaned modules removed so the directory tree reflects what's actually wired, not aspirational or abandoned code.
- Config consolidation follows the general "single source of truth" constraint implicit in avoiding vendor/config drift, even though it isn't named verbatim in `ARCHITECTURE.md`.
- **"AI never bypasses deterministic validation"** — the `critic_reviews` fix directly serves this: before the fix, the deterministic (rule-based) critic's verdict could be invisibly discarded, meaning the AI critic's opinion was the only one a reviewer ever saw. That's the exact failure mode the "Rules → AI → Validation → Human Review" principle exists to prevent.

---

## 7. Relevant Anthropic / CCAF Concepts

- **Behavior-preserving refactoring under verification**: the `LLMAgent` extraction is a textbook case for demonstrating that an agent abstraction can be refactored without changing observable behavior — verified here by comparing generated prompts character-for-character before/after, not just by inspection. This is directly relevant to designing reliable multi-agent systems (a recurring CCAF theme): shared harnesses reduce the surface area where individual agents can silently drift from each other.
- **Tool/agent contract minimalism**: `LLMAgent`'s subclass contract (`prompt_template`, `get_input`, `store_result`) is intentionally the smallest interface that captures what varies between agents — mirrors the general principle of keeping agent/tool definitions narrow and single-purpose rather than over-parameterized.
- **Shared mutable state between independent agents is a first-class failure mode in multi-agent systems**: two critics writing to the same `WorkflowState` field is structurally the same bug class as two tool calls writing to the same memory/scratchpad key in an agent harness — the fix (namespaced keys) is the general pattern, not a one-off.

---

## 8. Trade-offs

- **`README.md` reformatting** went slightly beyond literal "remove the corrupted lines" — it restored full markdown structure, since the file had zero markdown syntax and was unreadable as rendered output. This was judged to be squarely "fixing corruption" (format was demonstrably lost, per git history showing earlier commits had it) rather than a content redesign; no wording or sections were added/changed beyond that.
- **`services/__init__.py` export normalization was not propagated to call sites.** `workflows/workflow.py` and `agents/requirement_readiness_agent.py` still import services via direct submodule paths. Updating them would touch `workflow.py`'s existing deferred-import structure, which is explicitly tied to pending architecture decision #8 ("how workflow.py should model non-agent steps") — left alone to avoid pre-empting that decision.
- **`services/requirement_intelligence_service.py`** was left in place despite being an empty, unreferenced file, because it wasn't part of the "confirmed dead code" set (its name implies unresolved intent, not confirmed dead scaffolding) — deliberately not swept up with the rest.
- **The `critic_review` fix used string keys, not an enum.** A proper enum/constant set for critic names would prevent a future typo from silently creating an orphaned third key, but that felt like over-engineering for two producers; flagged in §13 as the trigger condition for revisiting.
- Moving the scratch scripts to `scripts/dev/` plus renaming two of them is a slightly larger touch than a pure "move," but was necessary to actually achieve the goal (keeping them runnable, and preventing pytest from silently executing live-API scripts once `tests/` grows) rather than just relocating a problem.

---

## 9. Verification Performed

- **Dead-code deletions**: repo-wide grep for zero importers/references before each deletion, not assumed.
- **Config consolidation**: runtime check that `svc.model == OPENAI_MODEL`.
- **`LLMAgent` extraction**: scripted character-for-character comparison of generated prompts and state-field writes against the original per-agent f-string templates, plus a full end-to-end workflow re-run.
- **`critic_reviews` fix**: new `tests/test_critic_reviews.py` (`test_two_critics_do_not_overwrite_each_other`) asserts both `"requirement_readiness"` and `"testcase"` keys are present and independently readable after both agents run; `scripts/dev/smoke_workflow.py` asserts `len(result.critic_reviews) == 2` on every smoke run as a regression guard.

---

## 10. Risks Introduced or Removed

**Removed**
- Silent data loss: the deterministic critic's verdict disappearing before reaching the UI, with no test ever catching it — this was a real correctness bug shipping to reviewers.
- Import-time ambiguity from `services/__init__.py` only partially re-exporting its public surface.
- Config drift risk from two independent sources of the OpenAI model name.

**Introduced**
- `critic_reviews` keys are free-form strings (`"testcase"`, `"requirement_readiness"`), not an enum — a typo in a future critic's `store_result` would silently create an unlinked third key rather than raising an error. Low risk today (only two producers, both covered by the new test), but worth enumerating before a third critic is added.
- None of the refactors change externally observable behavior (verified per §9), so no new product-facing risk was introduced by the `LLMAgent` extraction or the service/file moves.

---

## 11. Rollback Strategy

Both commits (`dbaabf2`, `236259c`) are plain code changes with no data migration — `WorkflowState` is in-memory per workflow run, not persisted, so there is nothing to migrate backward. `git revert 236259c` cleanly restores the single-field `critic_review` (reintroducing the overwrite bug); `git revert dbaabf2` restores the pre-cleanup file layout and duplicated agent boilerplate. Reverting either is a normal, low-risk git operation — no follow-up data cleanup required either way.

---

## 12. Review Lesson

A bug logged as "known, deferred, needs an architecture decision" should still get re-examined for a minimal fix before being left in the backlog indefinitely — good review practice distinguishes "this needs a design decision" from "this needs four lines and a test." The `critic_reviews` fix shipped without waiting on the larger "reconcile two readiness verdicts" decision because namespacing by key doesn't foreclose that decision, it just stops data loss in the meantime.

---

## 13. Future Improvements

- Migrate the full 24-item backlog into `docs/PRODUCT_BACKLOG.md` (currently empty).
- Build out the real pytest suite in `tests/` now that `scripts/dev/` is clearly separated from anything pytest should collect (`tests/test_critic_reviews.py` is the first real entry).
- Resolve `services/requirement_intelligence_service.py`'s intent (build vs. delete).
- If a third critic is ever added, replace `critic_reviews`'s free-form string keys with an enum/constant set (§8, §10).
- All remaining pending architecture decisions from the prior review remain open and unaffected by this wave (see `MASTER_CONTEXT.md` §6) except decision #3, which this wave's minimal fix partially addresses (see §4).

---

## 14. Proposed `MASTER_CONTEXT.md` Updates

Per `MASTER_CONTEXT.md`'s own rule, it was **not** edited directly. Proposed changes below, pending approval:

**Added**
- A line under §3 (Current Implementation State) noting that config now has a single source of truth (`config/settings.py`), PII masking reports accurate counts, and dead/orphaned modules (`sqlite_store.py`, `models/schemas.py`, `services/requirement_service.py`, empty stub agents, `requirement_engine/constants.py`, `services/logger_service.py`) have been removed.
- A note that `agents/base_agent.py` now provides a shared `LLMAgent` base class used by `UIAnalysisAgent`, `ImpactAnalysisAgent`, `TestcaseGenerationAgent`, and `CriticAgent`.
- A note that root-level scratch scripts now live in `scripts/dev/` (two renamed to `smoke_*.py` to avoid pytest auto-collection).
- A note that the wave-record convention now lives in `docs/waves/` (see `docs/waves/README.md`) and `docs/LESSONS_LEARNED.md` is the cross-wave synthesis — supersedes this document's own §3/§8 assumption that docs were purely ad hoc.

**Changed**
- §3's "Known dead code" list should be updated to remove the now-deleted items and add a note that `services/requirement_intelligence_service.py` remains as an open, undecided stub (not swept up).
- §3's "Known correctness bug" (`critic_review` overwrite) should be marked **resolved** — replaced by `critic_reviews`, covered by `tests/test_critic_reviews.py`.
- §5 (Active Backlog) Refactoring category: mark the 6 refactoring items and the `openai_service.py`/`config/settings.py` consolidation and PII-count bug as done.
- §6 pending decision #3 ("Reconciling the two independent 'readiness' verdicts") should note that the *data-loss* half of this problem is resolved (both verdicts now coexist); the *reconciliation/UX* half (how a reviewer should read two verdicts together) remains open.

**Removed**
- The 4 "Immediate Bug" backlog entries for `requirements.txt`, `README.md`, PII count, and OpenAI config — resolved.
- The dead-code refactoring entry — resolved (with the `requirement_intelligence_service.py` carve-out noted above).

**Why the change is required**: `MASTER_CONTEXT.md` §3/§5/§6 currently describe a pre-Wave-1 snapshot; leaving it unedited after this session would make it actively misleading for the next Claude session (it would re-flag already-fixed bugs and already-deleted files as open work, and misstate decision #3 as fully open).

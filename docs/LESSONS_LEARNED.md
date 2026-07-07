# Engineering & CCAF Learning Log

This is the evergreen, cross-wave revision guide — for CCAF prep, interviews,
and future architecture discussions. It is not a duplicate of the per-wave
records in `docs/waves/`: those capture the point-in-time "what changed and
why"; this file captures the small number of patterns from each wave worth
remembering *after* the wave itself is old news. Not everything from a wave
gets promoted here — only what generalizes.

Each entry is tagged with the categories it touches and links back to its
source wave. Tag vocabulary: **CCAF** · **Enterprise architecture** ·
**AI engineering** · **QA engineering** · **Python** · **Interview value** ·
**Practical engineering lesson** · **Code review lessons** ·
**Git workflow lessons**. When a new wave surfaces a pattern already listed
here, add a "Recurs in" reference rather than writing a new entry.

---

## Entry: Execution Tracking & Observability

**Source:** pre-Wave-1 (2026-06-07), `WorkflowState`/`ExecutionRecord` design.

**Tags:** Python · Enterprise architecture · QA engineering

**What was learned:**
1. Dataclasses can be used to model execution metadata.
2. `WorkflowState` can store execution history, not just final results.
3. Enterprise applications need traceability — knowing *what ran, in what
   order, with what outcome* is a separate concern from logging.
4. IST timestamps can be generated using `zoneinfo` rather than a
   third-party dependency.
5. Indentation mistakes in Python can silently break workflow logic (no
   compiler to catch a misplaced block).
6. `ExecutionRecord` evolved from `agent_name + status` to
   `agent_name + status + timestamp` — schemas grow as questions get asked
   of the data ("when did this run?" wasn't answerable until the timestamp
   was added).
7. **Traceability is different from logging.** Logging = messages for
   humans debugging in the moment. Traceability = structured execution
   history, queryable after the fact.
8. Observability helps identify slow or failing components before they
   become user-facing incidents.

**Why this approach vs. alternatives:** a dataclass-based in-memory record
was chosen over a logging framework or a database table because the data
is structural (agent, status, timestamp) rather than free text, and nothing
yet required it to survive past a single run.

**Interview value:** distinguishing traceability from logging is a good
answer to "how would you make a multi-step pipeline debuggable" — most
candidates only mention logging.

---

## Entry: Behavior-Preserving Refactoring via Verification, Not Inspection

**Source:** `docs/waves/WAVE_1.md` §4, §7, §9 (`LLMAgent` extraction).

**Tags:** CCAF · Enterprise architecture · AI engineering · Python ·
Interview value

**What was learned:** four agent classes (`UIAnalysisAgent`,
`ImpactAnalysisAgent`, `TestcaseGenerationAgent`, `CriticAgent`) were
identical constructor → build-prompt → call-LLM → store-on-state wiring
with only the prompt template and a couple of methods varying. Collapsing
them into a shared `LLMAgent` base is a routine Template Method refactor —
the part worth remembering is *how it was verified*: a scripted
character-for-character comparison of generated prompts and state writes
against the original per-agent code, not just "it looks equivalent."

**Why this approach vs. alternatives:** a metaclass or decorator-based
solution could also collapse the duplication, but would have obscured the
control flow for a marginal reduction in boilerplate — rejected per
`ENGINEERING_PRINCIPLES.md` #10 (Maintainability Over Cleverness).

**Recurs in:** the same "shared harness reduces agent drift" idea applies
to any future agent added to this codebase — new agents should default to
extending `LLMAgent`, not writing their own wiring.

**Interview value:** "how do you refactor with confidence, without a full
test suite in place" — the answer here is scripted output-diffing as a
substitute for missing test coverage, which is a real technique, not just
"I was careful."

---

## Entry: Namespaced State Keys Prevent Silent Multi-Agent Overwrites

**Source:** `docs/waves/WAVE_1.md` §4, §7, §10 (`critic_review` →
`critic_reviews` fix).

**Tags:** CCAF · Enterprise architecture · AI engineering · QA engineering ·
Python · Interview value

**What was learned:** two independent critics (a deterministic
rule-based one and an AI one) wrote to the same single field on shared
`WorkflowState`. Whichever ran second won, and the other's verdict vanished
with no error, no test, and no visible sign anything was wrong — the UI
just quietly showed one opinion instead of two. The fix was a dict keyed
by critic name, not a schema redesign.

**Why this approach vs. alternatives:** the "correct" long-term fix is an
architecture decision about how two readiness verdicts should be
reconciled and presented (still open, see `MASTER_CONTEXT.md` §6 decision
#3). Namespacing by key was chosen over waiting for that decision because
it fixes the data-loss bug without foreclosing the larger UX question —
recognizing when a small fix and a big decision are actually separable is
itself the lesson.

**Recurs in:** this is the generic failure mode of shared mutable state
between independent agents/tools in *any* multi-agent system — two tool
calls writing to the same memory key, two subagents appending to the same
scratchpad slot. The fix pattern (namespace by producer identity) is
general, not specific to this codebase.

**Interview value:** a strong answer to "what goes wrong in multi-agent
systems that doesn't show up in single-agent testing" — shared state
collisions are invisible until two agents run in the same execution and
one overwrites the other; this is a real, shipped example rather than a
hypothetical.

---

## Entry: Config Single Source of Truth

**Source:** `docs/waves/WAVE_1.md` §4 (`config/settings.py` /
`services/openai_service.py` consolidation).

**Tags:** Enterprise architecture · Python

**What was learned:** a config module existed, defined the right
constants, and was never imported — a second file independently re-derived
the same values via `os.getenv()` with a hardcoded fallback. Two sources of
truth for the same value drift silently; the fix is always "pick one,
delete the other," not "keep both in sync."

**Why this approach vs. alternatives:** no alternative considered —
config duplication has no legitimate use case in a single-process app.

**Interview value:** minor on its own, but a clean example of "unused code
isn't neutral — it's a second source of truth waiting to drift."

---

## Entry: A Correctness Bug Can Be Separable From Its Design Decision

**Source:** `docs/ARCHITECTURE_DECISIONS.md` ADR-002; `docs/waves/WAVE_1.md`
§4, §8, §10.

**Tags:** CCAF · Enterprise architecture · AI engineering · Code review
lessons · Practical engineering lesson · Interview value

**What was learned:** the `critic_review` overwrite bug had been deferred
because "fixing it properly" seemed to require an architecture decision
(how should two independent verdicts be reconciled for a human reviewer?).
On review, the *data-loss* part (one verdict silently vanishing) and the
*reconciliation-UX* part (how a reviewer should read two verdicts together)
turned out to be separable — namespacing the dict by critic name fixes the
former without deciding the latter.

**Why this approach vs. alternatives:** the tempting alternative was to
either wait indefinitely for the full design decision, or to make the UX
call unilaterally while "just fixing the bug." Both were rejected — see
ADR-002 for the full alternatives list.

**Recurs in:** any time a bug report says "the real fix needs a redesign."
Good review practice checks whether the *symptom* (data loss, a crash, a
silent failure) can be resolved independently of the *design question*
(how should this ideally work) before accepting an indefinite deferral.

**Interview value:** a strong, concrete answer to "how do you unblock a bug
fix that's stuck behind a bigger architecture decision" — most candidates
either wait or over-reach; separating the two is the actual skill.

---

## Entry: Reuse-Before-Create Applies to Documentation, Not Just Code

**Source:** `docs/ARCHITECTURE_DECISIONS.md` ADR-003; `docs/waves/WAVE_1.md`.

**Tags:** Enterprise architecture · Code review lessons · Git workflow
lessons · Practical engineering lesson · Interview value

**What was learned:** asked to create two new recurring documentation
artifacts, the right first move was the same instinct engineers apply to
code — check what already exists before adding something new. Two existing,
half-realized docs (`IMPLEMENTATION_CHANGES.md`, `LESSONS_LEARNED.md`)
already covered most of what was requested; creating two more parallel
docs would have produced three sources of truth narrating the same "why"
for the same change, with no mechanism keeping them consistent.

**Why this approach vs. alternatives:** see ADR-003. The key move was
presenting the reasoning and alternatives *before* implementing, and
getting explicit sign-off on a structure that didn't literally match the
original request — rather than either blindly complying (more doc drift)
or silently substituting a different structure without asking.

**Git workflow lesson:** the doc restructuring was committed separately
from the code bug fix (`3b84d25` vs `236259c`), even though both happened
in the same session — keeping commits scoped to one concern makes each
one independently revertable and reviewable, and `git mv` was used for the
file rename specifically to preserve history (`git log --follow` still
finds `WAVE_1.md`'s pre-rename commits).

**Interview value:** "how do you handle a request that, if implemented
literally, would create technical debt" — the answer is: implement the
intent, not the literal ask, but only after surfacing the trade-off and
getting sign-off, not by unilaterally deciding you know better.

---

## Entry: Decisions vs. Execution — the Seam That Keeps a Runtime Reusable

**Source:** `docs/ARCHITECTURE_DECISIONS.md` ADR-004; `docs/waves/WAVE_2.md`
(Workflow Governance Layer).

**Tags:** CCAF · Enterprise architecture · AI engineering · Python ·
Interview value

**What was learned:** the first draft of a governance/gate design put a
configurable `CriticGate(verdict_key=..., thresholds=...)` class inside
the reusable runtime layer, parameterized per-Skill. It looked reusable,
but it still had the runtime reaching into named business fields
(`confidence`, `needs_sme`) — just via configuration instead of
hardcoding. The fix was not "make it more generic," it was moving the
*interpretation* of those fields entirely out of the runtime: the Critic
exposes a `to_gate_decision()` method that returns a small neutral
contract (`GateDecision`), and the runtime's `GateEngine` only ever reads
that contract. The tell that the first design was wrong wasn't a bug —
it was that the runtime's source code still had to know a business
concept's *name* to be configured.

**Why this approach vs. alternatives:** see ADR-004 (B). A generic,
parameterized class inside the runtime is a subtler version of the same
mistake as hardcoding — both require the runtime to know what "approved"
or "confidence" mean. A neutral contract (produced by whoever holds the
domain knowledge, consumed by whoever enforces it) is the only version
where the runtime is provably domain-blind by inspection alone.

**Recurs in:** any "policy engine" / "rules runtime" design — the test
"does my reusable layer's source contain the name of a business field"
generalizes past this codebase. If yes, the boundary is in the wrong
place, no matter how configurable it looks.

**Interview value:** a concrete answer to "how do you design a reusable
policy/gating layer without coupling it to the business logic it
governs" — most candidates reach for configuration as the reuse
mechanism; the stronger answer is a produced/consumed contract.

---

## Entry: Testing Multi-Agent Control Flow Without Live Model Calls

**Source:** `docs/waves/WAVE_2.md` §7, §10 (`tests/test_workflow_gating.py`).

**Tags:** QA engineering · AI engineering · Python · Practical engineering
lesson · Interview value

**What was learned:** proving "the workflow halts correctly when a
Critic's verdict says it should" does not require a real LLM call, and
arguably shouldn't use one — an AI response is non-deterministic, so a
test built on a real call is really testing "did the API happen to
return something like X today," not "does the control flow correctly
handle X." Mocking the one deterministic seam (`ReadinessService.analyze`)
let four end-to-end tests exercise the *real* `WorkflowOrchestrator`
across every gate outcome (proceed, `NEEDS_SME`, `FAILED_VALIDATION`,
`PAUSED_FOR_REVIEW`) in under a second, with zero network dependency.

**Why this approach vs. alternatives:** mocking the LLM service itself
(`OpenAIService.generate`) was considered but rejected for this
particular test — the seam that actually determines gate behavior is the
deterministic `ReadinessService`, not the LLM call three layers away from
it. Mocking at the seam closest to the behavior under test kept the test
narrow and resistant to unrelated refactors elsewhere in the agent chain.

**Recurs in:** any agentic system where a deterministic rules layer feeds
a decision into AI-driven orchestration — the rules layer is almost
always the right place to inject test doubles, since it's what makes the
system's *control flow* deterministic even when its *content generation*
isn't.

**Interview value:** "how do you test an AI pipeline without flaky,
expensive, non-deterministic live calls" — identify the deterministic
seam nearest to the behavior under test, not the seam nearest to the AI
call.

---

## Entry: A Reusable Layer's Extension Points Should Predate Its First Extension

**Source:** `docs/waves/WAVE_2.md` §7, §13 (`WorkflowStep.critical`,
`BaseAgent.gate_check()`).

**Tags:** Enterprise architecture · Practical engineering lesson ·
Interview value

**What was learned:** `WorkflowStep.critical` (graceful degradation for
non-critical steps) and `BaseAgent.gate_check()` (an optional hook every
agent gets, defaulting to "no opinion") were both built into Wave 2 even
though no current Skill needs `critical=False` and only one Skill uses
`gate_check()`. This is deliberate, not speculative: the cost of adding
an unused optional flag/hook now is near zero, while retrofitting it
after three Skills already assume the loop's current shape is a much
larger change. The discipline is distinguishing "build the seam" (cheap,
done now) from "build the feature that uses the seam" (deferred until a
real consumer exists) — the latter is what "avoid speculative
implementation" actually warns against, not the former.

**Why this approach vs. alternatives:** the alternative — wait until a
non-critical Skill or a second gated Skill actually exists, then
refactor `workflow.py` again — was rejected because it repeats the exact
anti-pattern this wave was approved to fix (the orchestrator needing an
edit every time governance requirements grow).

**Recurs in:** any framework/runtime code written ahead of its second
use case — the generalizable test is "does this extension point cost
anything to have and nothing to use," not "will something use it soon."

**Interview value:** answers "how do you avoid both over-engineering and
under-engineering a new internal framework" — the line isn't
speculative vs. non-speculative, it's cheap-and-unused vs.
expensive-and-unused.

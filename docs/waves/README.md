# Wave Records — Convention

Each completed implementation wave gets one file here: `WAVE_N.md`. A wave
record is written once, when the wave is approved, and is not rewritten
afterwards — if a bug from Wave 1 gets fixed during Wave 3, that fix is
documented in `WAVE_3.md` with a cross-reference back, not by editing
`WAVE_1.md`. History stays honest about what was known at the time.

This is the detailed, point-in-time engineering record — "what changed and
why, for this wave, right now." The evergreen, cross-wave synthesis (which
patterns recur, which concepts each wave exercised, interview framing) lives
in `../LESSONS_LEARNED.md` instead, so the two don't duplicate each other:
wave files are the raw material, `LESSONS_LEARNED.md` is the distillation.

## Required sections, in order

1. **Scope** — what was approved for this wave, what was explicitly excluded.
2. **Files Changed** — grouped by category (bugs / refactoring / features).
3. **Business Problem Solved** — the real-world QA/engineering problem this
   wave addresses, not just the technical change.
4. **Why Each File Changed** — the reasoning, one entry per file/group.
5. **Engineering Principles Applied** — cite `ENGINEERING_PRINCIPLES.md` by
   number.
6. **Architecture Principles Applied** — cite `ARCHITECTURE.md` by name.
7. **Relevant Anthropic / CCAF Concepts** — what this wave teaches about
   building reliable agent systems.
8. **Trade-offs** — what was deliberately left undone or done differently
   than the "ideal" version, and why.
9. **Alternatives Considered** — for each non-trivial decision in this wave,
   the options that were rejected and why, and why the chosen option won.
   If a decision required Product Owner / Architect approval, give it a
   full entry in `docs/ARCHITECTURE_DECISIONS.md` instead of just this
   section, and link to it here rather than duplicating the reasoning.
10. **Verification Performed** — what was actually run/checked to confirm
    the change works (tests, manual runs, comparisons) — not just "should
    work."
11. **Risks Introduced or Removed** — what could break because of this
    wave, and what previously-risky thing this wave eliminated.
12. **Rollback Strategy** — how to undo this wave if it turns out to be
    wrong (usually: revert the commit(s); note anything that makes it *not*
    that simple, e.g. data migrations).
13. **Review Lesson** — one or two sentences on what this wave teaches
    about conducting a high-quality review of this kind of change. This is
    the sentence most likely to get promoted into `LESSONS_LEARNED.md`.
14. **Future Improvements** — near-term follow-ups surfaced by this wave.
15. **Proposed `MASTER_CONTEXT.md` Updates** — `MASTER_CONTEXT.md` is never
    edited directly except with explicit sign-off (see its own header);
    every wave proposes its diff here and waits for approval.

## Relationship to `docs/ARCHITECTURE_DECISIONS.md`

Not every decision in a wave needs a formal ADR — most belong in §9
(Alternatives Considered) or §8 (Trade-offs) inline. Promote a decision to
a full ADR when it (a) required Product Owner/Architect sign-off, (b)
changes a data contract, workflow behavior, or documentation structure
other waves will build on, or (c) is likely to be revisited later and the
reasoning needs to survive independently of this wave's file.

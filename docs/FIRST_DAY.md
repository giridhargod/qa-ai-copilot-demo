# First Day — Contributing to QA AI Copilot

This is the single entry point for a new contributor joining specifically to draft **Knowledge Packs** (see `docs/KNOWLEDGE_PACKS.md`). It assumes no prior context on the codebase and is written to need minimal reading and minimal local setup.

> If the contributor's Claude Code session won't have this repo cloned or browsable at all, hand them `docs/KNOWLEDGE_PACK_BRIEF.md` instead — it's a self-contained version of this same guidance with no cross-references to other repo files.

## Your role

You're a **Knowledge Pack Contributor**. You are not implementing application code, and you are not making architecture decisions — both of those stay with Giri and ChatGPT (the project's "C² Engineering Workflow," see `docs/C2_ENGINEERING_WORKFLOW.md`). Your job is to research, draft, and propose domain knowledge (rules, standards, thresholds) as Knowledge Pack files, and get them merged through a normal fork → PR → review cycle.

Nothing you merge goes live automatically — see `docs/KNOWLEDGE_PACKS.md` §4. Right now, Knowledge Pack content is reviewed and stored, not yet wired into running code.

## You do not need a full local setup

This project's Python app (Streamlit, OCR, OpenAI calls) is **not** something you need to install or run. Knowledge Packs are plain text/YAML files — authoring them needs nothing beyond Git and a text editor.

Concretely, skip all of this:
- Do **not** create a Python virtual environment.
- Do **not** run `pip install -r requirements.txt`.
- Do **not** install Tesseract OCR.

The repository itself is small (~7 MB excluding `.git`), so storage was never really the constraint — the Python environment would have been. Since you're skipping that entirely, a normal clone is fine.

### Option A — zero local storage (recommended)

1. Fork the repo on GitHub (button on the repo page).
2. On your fork's GitHub page, press `.` (period key) — this opens a full browser-based VS Code (github.dev), no local clone at all.
3. Create/edit files directly in the browser, commit, and push — all still inside your fork.
4. Open a PR from your fork's branch back to the upstream `main`.

### Option B — lightweight local clone (if you prefer local VS Code)

```
git clone --depth 1 https://github.com/<your-username>/qa-ai-copilot.git
cd qa-ai-copilot
git checkout -b knowledge/<short-topic-name>
```

`--depth 1` skips the full commit history — you only need the current files. Work only inside `knowledge/` (new files) and `docs/`. Don't create a venv, don't run the app.

## Branch and PR workflow

1. One branch per Knowledge Pack, named `knowledge/<topic>` (e.g. `knowledge/banking-kyc-rules`).
2. Add your pack under `knowledge/<domain>/<pack_name>.yaml` following the format in `docs/KNOWLEDGE_PACKS.md` §3.
3. Commit, push to **your fork**, then open a PR against the upstream repo's `main`.
4. Do not push directly to `main` and do not merge your own PR — Giri and/or ChatGPT review every Knowledge Pack PR before merge (same review bar as any other change to this project).
5. If Giri is unavailable for a stretch, PRs can queue — leave them open rather than merging without review.

## What to read first (in this order, skip everything else)

1. `README.md` — project overview, 2 minutes.
2. `docs/KNOWLEDGE_PACKS.md` — what a Knowledge Pack is, why it matters, the proposed file format.
3. `docs/CLAUDE.md`, the "Knowledge Packs" and "Privacy & Security" sections — house philosophy on what belongs in a pack and what doesn't.

You do **not** need `docs/MASTER_CONTEXT.md`, `docs/ARCHITECTURE.md`, or `docs/waves/*` — those document the implementation history and internal engineering decisions; they're not required to draft domain content.

## Ground rules

- Knowledge Packs contain **deterministic domain knowledge only** — rules, standards, regulations, thresholds. Never code, never prompts, never business logic implementation.
- Always cite a source (`source:` field). If you're not sure a rule is accurate, write `source: "needs SME verification"` rather than guessing — never invent a regulation.
- Never include real customer data, PII, or anything confidential — this is a public git history.
- One domain/rule-set per file; keep packs small and focused rather than one giant file per industry.

## Questions

Leave comments directly on your PR. Giri will review when available; non-urgent PRs are expected to wait rather than get merged unreviewed.

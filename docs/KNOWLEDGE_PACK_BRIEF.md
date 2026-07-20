# Knowledge Pack Contributor Brief (self-contained)

**Give this exact file to a contributor whose Claude Code session has no clone of this repository.** Everything needed is inline — no other file in this repo needs to be read. (If you *do* have the repo cloned or browsable, `docs/KNOWLEDGE_PACKS.md` and `docs/FIRST_DAY.md` are the canonical, more detailed versions of this same content — this file is the portable export of both, for a zero-access-to-the-repo starting point.)

Repo: **https://github.com/giridhargod/qa-ai-copilot-main**

---

## 1. What this project is (one paragraph)

QA AI Copilot is an AI-powered Quality Engineering platform: it turns requirements, screenshots, and documents into structured QA artifacts (test cases, impact analysis, traceability, coverage) using a multi-agent workflow, with a strict philosophy of **Rules → AI → Validation → Human Review** — AI never gets the final word, deterministic rules and a human always do.

## 2. Your task: Knowledge Packs — what and why

A **Knowledge Pack** is a small, versioned file holding **deterministic domain knowledge** — never code, never AI prompts, never business logic. Examples: banking/KYC rules, telecom provisioning rules, insurance underwriting rules, accessibility standards, API testing rules, performance thresholds, security testing rules.

**Why it matters:** the project's stated goal is to support any industry (banking, healthcare, telecom, insurance...) by *adding a Knowledge Pack file*, not by changing code. Right now, all domain rules are hardcoded directly in Python — Knowledge Packs are how that gets replaced with something maintainable. Your contribution is pure content/research work: it does not touch the application code at all.

**Important — this is a draft/proposed format**, not yet approved by the project's architecture reviewer (ChatGPT, in this project's "C² workflow" — see repo's `docs/MASTER_CONTEXT.md` if you ever do get repo access). It's good enough to draft real content against now; the schema may be revised later without losing your content.

## 3. The format

```
knowledge/
  <domain>/
    <pack_name>.yaml
```

Example path: `knowledge/banking/kyc_verification_rules.yaml`

```yaml
pack_id: banking.kyc_verification_rules
domain: banking
version: 0.1.0
description: >
  Deterministic rules for validating KYC (Know Your Customer)
  requirement completeness before a requirement is marked ready.
source: "RBI KYC Master Direction, 2016 (summarized, non-legal)"
maintainer: <your-github-username>

rules:
  - id: kyc-001
    description: "PAN number format must be validated before account activation"
    keywords: ["PAN", "permanent account number"]
    severity: mandatory

  - id: kyc-002
    description: "Address proof must be dated within 90 days"
    keywords: ["address proof", "utility bill"]
    severity: mandatory
```

Field rules:
- `pack_id` — dotted, unique, stable once merged.
- `version` — bump on any content change (patch = wording, minor = rule added, major = rule removed/renamed).
- `source` — always cite where the rule came from. If unsure, write `source: "needs SME verification"` — never invent a regulation.
- `severity` — `mandatory` / `recommended` / `informational`.
- No PII, no real customer/company data — this is a public git history.
- One domain/rule-set per file. Keep packs small and focused, not one giant file per industry.

## 4. How to submit — no local clone, no git commands needed

1. Go to **https://github.com/giridhargod/qa-ai-copilot-main** and click **Fork** (top right) — creates your own copy under your GitHub account.
2. On your fork, click **Add file → Create new file**.
3. Type the path as the filename, e.g. `knowledge/banking/kyc_verification_rules.yaml` — GitHub creates the folders automatically.
4. Paste your YAML content (draft it with Claude Code locally first if you like — just paste the finished text here, nothing needs to run).
5. Scroll down, choose **"Create a new branch and start a pull request"** (not the default "commit directly to main" option), name the branch e.g. `knowledge/banking-kyc-rules`, and click **Propose new file**.
6. GitHub takes you to a PR screen comparing your fork's new branch against the upstream repo's `main`. Fill in a short title/description and click **Create pull request**.

That's the entire workflow — everything happens in the browser, on GitHub's servers. No disk space used, no git installed or run.

## 5. Using Claude Code to help draft content

You can absolutely use Claude Code to research and draft the YAML content — just run it in any empty local folder (it doesn't need this repo at all). Good prompts:

- "Help me draft a Knowledge Pack YAML file for [domain] following this schema: [paste §3 above]. The rules should cover [topic]."
- "Review this Knowledge Pack YAML for internal consistency and check I've cited a source for every rule."

Then copy the final YAML text into GitHub's web editor as in §4. Claude Code is your drafting assistant here, not something that needs to touch the actual repository.

## 6. Review

Every PR is reviewed by Giri and/or ChatGPT before merge — nothing merges automatically, and PRs may sit for a while unreviewed if Giri is unavailable. That's expected; leave comments on the PR with any questions.

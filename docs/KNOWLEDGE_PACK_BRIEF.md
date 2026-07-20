# Knowledge Pack Contributor Brief (self-contained)

**Give this exact file to a contributor whose Claude Code session has no clone of this repository.** Everything needed is inline — no other file in this repo needs to be read. (If you *do* have the repo cloned or browsable, `docs/KNOWLEDGE_PACKS.md` and `docs/FIRST_DAY.md` are the canonical, more detailed versions of this same content — this file is the portable export of both, for a zero-access-to-the-repo starting point.)

Repo: **https://github.com/giridhargod/qa-ai-copilot-main**

---

## 1. What this project is (one paragraph)

QA AI Copilot is an AI-powered Quality Engineering platform: it turns requirements, screenshots, and documents into structured QA artifacts (test cases, impact analysis, traceability, coverage) using a multi-agent workflow, with a strict philosophy of **Rules → AI → Validation → Human Review** — AI never gets the final word, deterministic rules and a human always do.

## 2. Your task: Knowledge Packs — what and why

A **Knowledge Pack** is a small, versioned file holding **deterministic domain knowledge** — never code, never AI prompts, never business logic. Examples: banking/KYC rules, telecom provisioning rules, insurance underwriting rules, accessibility standards, API testing rules, performance thresholds, security testing rules.

**Why it matters:** the project's stated goal is to support any industry (banking, healthcare, telecom, insurance...) by *adding a Knowledge Pack file*, not by changing code. Right now, all domain rules are hardcoded directly in Python — Knowledge Packs are how that gets replaced with something maintainable. Your contribution is pure content/research work: it does not touch the application code at all.

**This format is approved** by the project's architecture reviewer (ChatGPT, in this project's "C² workflow") as of 2026-07-20. Follow the section/field names below exactly — don't rename, reorder, or invent sibling fields — a schema validator is planned and will assume this exact shape.

## 3. The format

### 3.1 Directory layout — domain → capability → pack

```
knowledge/
  <domain>/
    manifest.yaml
    <capability>/
      <pack_name>.yaml
```

Example:

```
knowledge/
  banking/
    manifest.yaml
    kyc/
      verification_rules.yaml
```

`pack_id` convention: `<domain>.<capability>.<pack_name>`, e.g. `banking.kyc.verification_rules`.

### 3.2 Pack file — five sections: metadata, knowledge, rules, examples, references

```yaml
metadata:
  pack_id: banking.kyc.verification_rules
  domain: banking
  capability: kyc
  version: 0.1.0
  description: >
    Deterministic rules for validating KYC (Know Your Customer)
    requirement completeness before a requirement is marked ready.
  owner: <your-github-username>
  review_status: draft        # draft | reviewed | approved | deprecated
  lifecycle: active            # active | deprecated | retired
  created_at: "2026-07-20"
  updated_at: "2026-07-20"

knowledge:
  - id: kyc-fact-001
    statement: >
      PAN (Permanent Account Number) is a 10-character alphanumeric
      identifier issued by India's Income Tax Department.
  - id: kyc-fact-002
    statement: "Address proof documents are valid only within a defined recency window."

rules:
  - id: kyc-001
    description: "PAN number format must be validated before account activation"
    based_on: [kyc-fact-001]
    matching:
      type: keywords
      values: ["PAN", "permanent account number"]
    severity: mandatory

  - id: kyc-002
    description: "Address proof must be dated within 90 days"
    based_on: [kyc-fact-002]
    matching:
      type: keywords
      values: ["address proof", "utility bill"]
    severity: mandatory

examples:
  - input: "User must upload PAN card and a utility bill dated within the last 60 days."
    expected_rule_matches: ["kyc-001", "kyc-002"]

references:
  - type: regulation
    citation: "RBI KYC Master Direction, 2016 (summarized, non-legal)"
  - type: note
    citation: "needs SME verification where marked"
```

Field rules:
- **`metadata`** — identity + governance. `version` bumps on content change (patch = wording, minor = rule added, major = rule removed/renamed). `review_status` tracks human-review state; `lifecycle` tracks whether the pack is still meant to be live — these are independent of each other.
- **`knowledge`** — descriptive domain facts only. No matching, no severity.
- **`rules`** — the actionable checks. `based_on` links back to `knowledge` entry IDs. `matching` is typed (`type: keywords` today, with a `values` list) so other matching styles can be added later without breaking existing packs.
- **`examples`** — sample input text + which rule IDs should fire on it. Optional but encouraged.
- **`references`** — plural, each with a `type` (`regulation` / `standard` / `internal` / `note`) and `citation`. If unsure of a source, use `type: note, citation: "needs SME verification"` — never invent a regulation.
- No PII, no real customer/company data — this is a public git history.
- One capability/rule-set per file, not one giant file per industry.

### 3.3 `manifest.yaml` — one per domain

```yaml
domain: banking
description: "Banking industry Knowledge Packs"
packs:
  - pack_id: banking.kyc.verification_rules
    path: kyc/verification_rules.yaml
    enabled: true
    depends_on: []
```

`depends_on` is reserved for future cross-pack dependencies — leave `[]` for now.

## 4. How to submit — no local clone, no git commands needed

1. Go to **https://github.com/giridhargod/qa-ai-copilot-main** and click **Fork** (top right) — creates your own copy under your GitHub account.
2. On your fork, click **Add file → Create new file**.
3. Type the full path as the filename, e.g. `knowledge/banking/kyc/verification_rules.yaml` — GitHub creates the folders automatically. Also create/update `knowledge/banking/manifest.yaml` to list your new pack.
4. Paste your YAML content (draft it with Claude Code locally first if you like — just paste the finished text here, nothing needs to run).
5. Scroll down, choose **"Create a new branch and start a pull request"** (not the default "commit directly to main" option), name the branch e.g. `knowledge/banking-kyc-rules`, and click **Propose new file**.
6. GitHub takes you to a PR screen comparing your fork's new branch against the upstream repo's `main`. Fill in a short title/description and click **Create pull request**.

That's the entire workflow — everything happens in the browser, on GitHub's servers. No disk space used, no git installed or run.

## 5. Using Claude Code to help draft content

You can absolutely use Claude Code to research and draft the YAML content — just run it in any empty local folder (it doesn't need this repo at all). Good prompts:

- "Help me draft a Knowledge Pack YAML file for [domain/capability] following this schema: [paste §3.2 above]. The rules should cover [topic]."
- "Review this Knowledge Pack YAML for internal consistency, check every rule has a `based_on` knowledge entry, and check I've cited a reference for every rule."

Then copy the final YAML text into GitHub's web editor as in §4. Claude Code is your drafting assistant here, not something that needs to touch the actual repository.

## 6. Review

Every PR is reviewed by Giri and/or ChatGPT before merge — nothing merges automatically, and PRs may sit for a while unreviewed if Giri is unavailable. That's expected; leave comments on the PR with any questions.

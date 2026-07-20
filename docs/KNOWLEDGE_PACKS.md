# Knowledge Packs

**Status: v0.1 draft.** The "why" and "what" sections reflect settled project vision (`CLAUDE.md`, `ARCHITECTURE.md`, `MASTER_CONTEXT.md` §1–2). The **file format and loading mechanism proposed in §3–4 are NOT yet approved** — `MASTER_CONTEXT.md` §6 lists "Knowledge Pack mechanism" as an open architecture decision requiring ChatGPT (Architect) + Giri sign-off. This draft exists so content work can start now without waiting; treat the schema as provisional until the Architect reviews it.

---

## 1. What a Knowledge Pack is

A Knowledge Pack is a self-contained, versioned file (or small set of files) holding **deterministic domain knowledge** — never code, never AI prompts, never business logic:

- Banking / KYC / AML rules
- Telecom provisioning rules
- Insurance underwriting rules
- Accessibility standards (WCAG mappings)
- API testing rules
- Performance testing thresholds
- Security testing rules

Per `CLAUDE.md`: *"Knowledge Packs should evolve independently from workflows. Future AI assistance may recommend improvements but deterministic rules remain authoritative."*

## 2. Why this matters for QA AI Copilot specifically

Two things make this more than a nice-to-have:

1. **It's how the platform becomes industry-agnostic without touching code.** `MASTER_CONTEXT.md` §1: *"Target adoption is industry-agnostic (banking, healthcare, telecom, insurance, etc.) via domain knowledge added through Knowledge Packs, not code changes."* Onboarding a new industry should mean adding a pack, not forking the codebase.
2. **It's paying down a real, named debt.** `MASTER_CONTEXT.md` §3 states plainly: *"No `knowledge/` directory anywhere — all domain rules/taxonomies (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, reviewer keyword rules, every agent prompt) are hardcoded in Python."* This violates the project's own stable architecture rule (§2): *"Knowledge stays external to Skills via versioned Knowledge Packs — never hardcoded business rules."* Every Knowledge Pack drafted is a step toward closing that gap.

Knowledge Pack content is also the part of this project that scales well as **parallel, non-code contribution** — drafting a domain rule set doesn't require touching `agents/`, `governance/`, or any running code, so it's low-risk to work on independently while implementation work (Claude/Giri's side) continues separately.

## 3. Proposed format (draft — pending Architect approval)

```
knowledge/
  <domain>/
    <pack_name>.yaml
```

Example: `knowledge/banking/kyc_verification_rules.yaml`

Each pack is a single YAML file:

```yaml
pack_id: banking.kyc_verification_rules
domain: banking
version: 0.1.0
description: >
  Deterministic rules for validating KYC (Know Your Customer)
  requirement completeness before a requirement is marked ready.
source: "RBI KYC Master Direction, 2016 (summarized, non-legal)"
maintainer: <github-username>

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

Field notes:
- `pack_id` — dotted, unique, stable (used as a lookup key once wired into code — don't rename after merge without a version bump).
- `version` — bump on any rule content change (semver: patch = wording fix, minor = rule added, major = rule removed/renamed).
- `source` — always cite where a rule came from. Never fabricate a regulation; if unsure, write `source: "needs SME verification"` and flag it in the PR.
- `severity` — `mandatory` / `recommended` / `informational` (open to Architect revision).
- No PII, no real customer data, no company-confidential rules — these packs are versioned in a public-facing git history.

## 4. How Knowledge Packs get integrated (two phases)

**Phase 1 — now (content only).** Knowledge Pack PRs are reviewed for accuracy, sourcing, and format consistency. They land in `knowledge/` as approved, versioned, ready-to-wire assets. Nothing in the running code reads them yet.

**Phase 2 — after the Architect resolves `MASTER_CONTEXT.md` §6 decision #1 (loading strategy).** A future wave replaces the hardcoded constants named in §3 (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, etc.) with a loader that reads `knowledge/`. Content drafted in Phase 1 doesn't get thrown away — it's exactly what Phase 2 wires in.

Do not write code in `requirement_engine/`, `critics/`, or elsewhere to consume `knowledge/` yet — that step is explicitly gated on the open architecture decision.

## 5. Review flow

Same as any other contribution (see `docs/FIRST_DAY.md`): fork → branch → PR against `main` → reviewed by Giri and/or ChatGPT before merge. No direct pushes to `main`, no self-merging.

---

*Once the Architect reviews this draft, replace this status line and file the resulting diff the way any other `MASTER_CONTEXT.md`-adjacent decision gets recorded — see `docs/MASTER_CONTEXT.md`'s "How to Update This Document" section.*

# Knowledge Packs

**Status: v0.2 — direction and schema approved by the Architect (ChatGPT), 2026-07-20.** `MASTER_CONTEXT.md` §6 decision #1 ("Knowledge Pack mechanism") is resolved for the authoring format below. Still open: the concrete runtime loader (Phase 2, §4) and the schema-validation file itself (§3.4) — both explicitly planned, not yet built. Contributors should follow §3 exactly as written; it's stable enough to produce real content against.

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

## 3. Format (Architect-approved, 2026-07-20)

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
    aml/
      screening_rules.yaml
```

`pack_id` convention: `<domain>.<capability>.<pack_name>`, e.g. `banking.kyc.verification_rules`.

### 3.2 Pack file — five separated sections

Each pack file has exactly five top-level sections — `metadata`, `knowledge`, `rules`, `examples`, `references` — kept distinct so the schema can grow without breaking existing packs:

```yaml
metadata:
  pack_id: banking.kyc.verification_rules
  domain: banking
  capability: kyc
  version: 0.1.0
  description: >
    Deterministic rules for validating KYC (Know Your Customer)
    requirement completeness before a requirement is marked ready.
  owner: <github-username>
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

Section notes:
- **`metadata`** — identity + governance. `version` tracks content revisions (semver: patch = wording, minor = rule added, major = rule removed/renamed). `review_status` and `lifecycle` are separate axes: `review_status` tracks where the pack sits in human review; `lifecycle` tracks whether it's still meant to be live, independent of review state.
- **`knowledge`** — descriptive domain facts/definitions. No matching, no severity — just what's true in the domain.
- **`rules`** — the actionable, matchable checks. `based_on` links a rule back to the `knowledge` entries it derives from, for traceability. `matching` is a typed section, not a bare `keywords` list — today only `type: keywords` (with a `values` list) is defined, but the shape leaves room for `type: regex`, `type: field_presence`, etc. later without a breaking migration.
- **`examples`** — optional but encouraged: sample input text plus which rule IDs should fire on it. Doubles as a regression fixture once Phase 2 wires a loader.
- **`references`** — plural (replaces the old singular `source` field), each entry typed (`regulation` / `standard` / `internal` / `note`) with a `citation`. Never fabricate a regulation — use `type: note, citation: "needs SME verification"` when unsure.
- No PII, no real customer data, no company-confidential content — packs are versioned in a public-facing git history.

### 3.3 `manifest.yaml` — one per domain

Lists every pack in a domain, for discovery, dependency tracking, and future enable/disable without deleting content:

```yaml
domain: banking
description: "Banking industry Knowledge Packs"
packs:
  - pack_id: banking.kyc.verification_rules
    path: kyc/verification_rules.yaml
    enabled: true
    depends_on: []
  - pack_id: banking.aml.screening_rules
    path: aml/screening_rules.yaml
    enabled: true
    depends_on: []
```

`depends_on` is reserved for a future case (a pack relying on another domain's shared definitions) — leave it `[]` until that need is concrete.

### 3.4 Schema validation — planned, not yet built

A JSON Schema (or equivalent) for both the pack file and `manifest.yaml` is planned to run before Phase 2's runtime loader reads anything. It doesn't exist yet. Until it does: follow §3.2/§3.3's section and field names **exactly** — don't rename, reorder, or invent sibling fields — so validation, when added, doesn't require reformatting every existing pack.

## 4. How Knowledge Packs get integrated (two phases, both Architect-approved)

**Phase 1 — Knowledge Engineering (now, content only).** Knowledge Pack PRs are reviewed for accuracy, sourcing, and structural conformance to §3. They land in `knowledge/` as approved, versioned, ready-to-wire assets. Nothing in the running code reads them yet. This phase proceeds independently of Phase 2's timeline.

**Phase 2 — runtime integration (not yet started).** A future wave replaces the hardcoded constants named in §2 (`CATEGORY_KEYWORDS`, `MANDATORY_WORDS`, etc.) with a loader that reads `knowledge/`, validated against the schema in §3.4 once it exists. Content drafted in Phase 1 doesn't get thrown away — it's exactly what Phase 2 wires in.

Do not write code in `requirement_engine/`, `critics/`, or elsewhere to consume `knowledge/` yet — the loader design is still unbuilt.

## 5. Review flow

Same as any other contribution (see `docs/FIRST_DAY.md`): fork → branch → PR against `main` → reviewed by Giri and/or ChatGPT before merge. No direct pushes to `main`, no self-merging.

---

*This schema (v0.2) was approved by the Architect on 2026-07-20. The corresponding `MASTER_CONTEXT.md` update is proposed, not yet applied — see the session's proposed diff, pending Giri's sign-off per `MASTER_CONTEXT.md`'s "How to Update This Document" section.*

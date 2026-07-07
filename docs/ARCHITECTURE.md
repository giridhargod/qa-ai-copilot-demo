# QA AI Copilot — Architecture

## Architecture Overview

QA AI Copilot follows a modular, layered Enterprise AI architecture designed to assist software quality engineering through reusable Enterprise Skills, orchestrated Workflows, externalized Knowledge Packs, deterministic validation, AI reasoning, and Human Review.

The platform is intentionally designed to evolve from a Proof of Concept into a production-quality Enterprise AI Platform while remaining maintainable, extensible, vendor-neutral, and educational.

Internally, QA AI Copilot follows an **Agent-oriented Architecture**.

Externally, it exposes a **Skill-oriented Enterprise Platform**.

This separation allows implementation details to evolve without changing the business capabilities presented to users.

---

# Architectural Goals

The architecture is designed to maximize:

* Modularity
* Reusability
* Scalability
* Maintainability
* Explainability
* Extensibility
* Vendor neutrality
* LLM agnosticism
* Human governance
* Enterprise adoption

Every architectural decision should strengthen one or more of these goals.

---

# Architectural Layers

## Presentation Layer

Responsible for user interaction.

Examples:

* Streamlit UI (current)
* Future React UI
* Future Enterprise Portal
* Future Chat Interface
* Future API Consumers

Presentation components should never contain business logic.

---

## Workflow Layer

Responsible for orchestrating Enterprise Skills into complete business processes.

Responsibilities include:

* workflow execution
* orchestration
* workflow state
* execution tracking
* approvals
* metrics
* auditability

Workflows coordinate Skills but never implement business logic.

### Governance Runtime (`governance/`)

The concrete implementation of this layer's "approvals" and "auditability" responsibilities, introduced in Wave 2. Deliberately domain-blind: it executes decisions, it never makes them.

* `WorkflowStatus` / `GateDecision` — the shared vocabulary and contract Skills/Critics use to communicate a verdict to the runtime.
* `ExecutionGuard` / `RetryPolicy` — safe agent execution: catches failures, retries only caller-supplied transient exception types, produces an honest execution record instead of assuming success.
* `OutputValidator` — a minimal, domain-neutral AI-output contract (non-empty result) enforced before a Skill's output reaches workflow state.
* `GateEngine` / `WorkflowStep` — mechanically enforces whatever `GateDecision` a step's agent returns via an optional `gate_check()` hook; a step with no opinion always proceeds.

Business thresholds (e.g. what confidence counts as "approved") are never defined here — they live with the Critic/Skill that computes the verdict (see `critics/`), which then translates its own verdict into the neutral `GateDecision` contract. See `docs/ARCHITECTURE_DECISIONS.md` ADR-004 for the full reasoning.

---

## Skill Layer

The core business capability layer.

Every Skill solves exactly one business problem.

Examples include:

* Requirement Readiness
* Requirement Validation
* Requirement Classification
* Test Design
* Coverage Analysis
* Traceability
* Impact Analysis
* Automation Readiness
* QA Critic
* SME Escalation

Internally, a Skill may contain:

* Rule Engines
* AI Agents
* Validators
* Reviewers
* Evaluators
* Classifiers

These internal components remain implementation details and are not exposed directly to users.

---

## Knowledge Layer

Knowledge remains external to implementation.

Knowledge Packs provide:

* business rules
* regulations
* testing heuristics
* domain expertise
* platform-specific guidance
* enterprise standards

Skills consume Knowledge Packs but never hardcode business knowledge.

---

## Service Layer

Shared infrastructure used across multiple Skills.

Examples include:

* AI Provider Service
* OCR Service
* PII Protection Service
* Metrics Service
* Logging Service
* File Processing Service
* Storage Service
* Time Service

Services provide reusable infrastructure rather than business capabilities.

---

## Infrastructure Layer

Provides platform-level capabilities.

Examples include:

* LLM Providers
* Local Execution
* Future MCP Servers
* Future REST APIs
* Authentication
* Configuration
* Dependency Management

Infrastructure should remain replaceable with minimal impact on higher layers.

---

## Storage Layer

Responsible for persistence.

Examples include:

* SQLite
* Future PostgreSQL
* Vector Databases
* Object Storage
* Enterprise Data Stores

Storage implementations should remain abstracted from business logic.

---

# High-Level Data Flow

A typical enterprise workflow follows:

Document

↓

Requirement Extraction

↓

Requirement Readiness

↓

Workflow Orchestration

↓

Enterprise Skills

↓

Coverage & Traceability

↓

Evaluation

↓

Enterprise Critic

↓

Human Review (when required)

↓

Final Output

Every stage should produce explainable outputs and measurable quality indicators.

---

# AI Architecture

AI assists engineering decisions.

It does not replace them.

Every major workflow should follow:

Rules

↓

AI Reasoning

↓

Validation

↓

Human Review

AI recommendations should always remain explainable and reviewable.

---

# Human Review Architecture

Human Review is a first-class architectural capability.

It is available throughout the platform rather than existing only as the final step.

Any Skill may request:

* SME clarification
* Business validation
* Manual approval
* Risk assessment

Human Review should pause workflows only when required and allow execution to continue once resolved.

**Current implementation status (Wave 2):** the "pause" half is real — the Governance Runtime halts a workflow via `WorkflowStatus.PAUSED_FOR_REVIEW` / `NEEDS_SME` / `FAILED_VALIDATION` when a Skill's gate says to. The "allow execution to continue once resolved" half is not yet implemented — it requires a persistence strategy (still open, `MASTER_CONTEXT.md` §6 decision #9) so a paused run can be durably resumed rather than only halted-and-returned within a single request.

---

# Engineering Architecture (C² Workflow)

QA AI Copilot is developed using the C² Engineering Workflow.

Architecture

↓

ChatGPT

↓

Implementation

↓

Claude

↓

Verification

↓

ChatGPT

↓

Documentation

↓

Git Repository

↓

Continuous Learning

This workflow separates architectural decision-making from implementation while maintaining continuous verification and learning.

---

# Future Extension Points

The architecture intentionally supports future expansion through:

* New Enterprise Skills
* New Workflows
* Knowledge Packs
* MCP Servers
* AI Providers
* REST APIs
* React UI
* Mobile Clients
* Enterprise Integrations
* Additional Storage Providers

Future capabilities should integrate without requiring architectural redesign.

---

# Architectural Constraints

The following constraints intentionally guide development:

* Workflows orchestrate but do not implement business logic.
* Skills solve one business problem.
* Services provide shared infrastructure.
* Knowledge remains external to Skills.
* AI never bypasses deterministic validation.
* Human Review remains available throughout the platform.
* Components should avoid circular dependencies.
* Vendor lock-in should be avoided.
* Responsibilities should remain clearly separated.

---

# Architectural Evolution

The platform is expected to evolve through the following stages:

Proof of Concept

↓

Reusable Agents

↓

Enterprise Skills

↓

Enterprise Workflows

↓

Knowledge Packs

↓

Enterprise AI Platform

↓

Production Enterprise Product

Each stage should improve maintainability, enterprise readiness, and educational value without sacrificing simplicity.

---

# Definition of Done

The architecture is considered healthy when:

* Layers remain independent.
* Responsibilities remain clear.
* Skills remain reusable.
* Workflows remain orchestration-focused.
* Knowledge remains external.
* Services remain generic.
* AI remains optional.
* Human governance remains intact.
* New capabilities can be added without major redesign.
* The platform continues to educate the engineers who build and use it.

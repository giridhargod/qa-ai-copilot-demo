# QA AI Copilot

## Overview

QA AI Copilot is an AI-powered Quality Engineering assistant that transforms requirements, user stories, screenshots, PDFs, and application documentation into structured QA artifacts.

The platform helps QA engineers perform:

* Requirement Analysis
* Impact Analysis
* Test Design
* Traceability Mapping
* Coverage Analysis
* Quality Evaluation

using a multi-agent workflow architecture.

## Why This Project Exists

This project started as a personal learning initiative to better understand:

* Large Language Models
* Agent Architectures
* AI-assisted Quality Engineering
* Workflow Orchestration
* Enterprise AI Design Patterns

While exploring these concepts, the project gradually evolved from a simple testcase generator into a reusable QA-focused AI artifact.

Today it demonstrates how AI agents can assist quality engineering activities throughout the testing lifecycle.

## Business Problem

Quality Engineers spend significant effort on:

* Requirement analysis
* Impact assessment
* Test design
* Coverage validation
* Traceability preparation

These activities are often manual, repetitive, and difficult to scale.

QA AI Copilot accelerates these activities by providing AI-assisted analysis and artifact generation.

## Current Capabilities

### Requirement Analysis Agent

Extracts:

* Screens
* Components
* Actions
* Validations
* Business Rules
* Edge Cases

### Impact Analysis Agent

Identifies:

* Functional Impact
* UI Impact
* API Impact
* Database Impact
* Security Impact
* Integration Impact
* Regression Areas

### Test Design Agent

Generates:

* Positive Scenarios
* Negative Scenarios
* Boundary Tests
* Validation Tests
* Security Tests
* Accessibility Tests
* Regression Scenarios

### Critic Agent

Reviews generated artifacts and provides:

* Coverage Assessment
* Quality Feedback
* Missing Scenarios
* Improvement Recommendations

### Traceability Layer

Creates mappings between:

* Requirements
* Generated Test Cases

and enables coverage analysis.

### Evaluation Framework

Measures generated output quality using:

* Testcase Completeness
* Missing Fields
* Structural Validation
* Quality Scoring

### Execution Tracking

Captures workflow execution history including:

* Agent Executed
* Execution Status
* Timestamp

for improved observability.

## Secure Test Step Generator

`secure_test_step_generator/` is a self-contained package that turns a Word/PDF
document containing screenshots and tester notes into an enterprise test-step
Excel file, without ever sending a raw screenshot or unredacted sensitive data
to an LLM:

```
Document -> OCR -> Sanitization -> AI Step Generation -> Validation -> Excel Export
```

It does not import from the rest of this repository, so it can be copied out
and run on its own. See `secure_test_step_generator/README.md` for setup,
usage, and its documented security boundary and known limitations.

## Architecture

```
User Input
     │
     ▼
PII Processor
     │
     ▼
UI Analysis Agent
     │
     ▼
Impact Analysis Agent
     │
     ▼
Testcase Generation Agent
     │
     ▼
Critic Agent
     │
     ▼
Traceability Engine
     │
     ▼
Coverage Engine
     │
     ▼
Evaluation Engine
```

## Technology Stack

* Python
* Streamlit
* OpenAI
* OCR (Tesseract)
* PDF Processing
* DOCX Processing
* Dataclasses
* Pydantic

## Current Status

Current maturity level:

**Enterprise QA AI Copilot (Prototype / Innovation Artifact)**

The project is intended for:

* AI Engineering Learning
* QA Innovation Demonstrations
* Internal Hackathons
* AI Artifact Showcases
* Quality Engineering Experimentation

## Future Roadmap

* Intelligent Traceability Mapping
* RAG Integration
* Knowledge Base Search
* Multi-Modal Analysis
* Automated Validation Framework
* MCP Integration
* CLI Interface
* REST API Layer
* Agent Evaluation Benchmarks

## Author

Developed as part of a continuous learning journey focused on:

* AI Engineering
* Agentic Systems
* Enterprise Quality Engineering
* Workflow Automation

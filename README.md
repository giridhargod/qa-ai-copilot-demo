# QA AI Copilot

QA AI Copilot is an AI-powered software testing assistant built to help testers and developers analyze requirements, understand impacts, generate test cases, and improve test coverage using AI.

The project started as a learning exercise to explore Python, Generative AI, and agent-based workflows. Over time, it has evolved into a structured AI QA platform focused on real-world software testing use cases and enterprise-style architecture.

## Why I Built This

As a QA Engineer, I wanted to go beyond traditional automation and learn how AI can assist throughout the software testing lifecycle.

Instead of building small isolated demos, I chose to build a complete project that would help me learn:

* Python development
* AI application architecture
* Agent orchestration
* Workflow design
* Prompt engineering
* Software testing with AI
* Production-oriented project structure

The goal is to create a practical AI QA Copilot that demonstrates how AI can support requirement analysis, impact analysis, and test design activities.

## Current Capabilities

The platform currently supports:

* Requirement and user story analysis
* UI analysis from requirements
* Impact analysis
* Structured test case generation
* Test coverage review through a Critic Agent
* PDF document processing
* DOCX document processing
* OCR-based screenshot text extraction
* PII masking before AI processing
* Agent-based workflow execution
* Workflow state management
* Execution traceability logging

## Current Architecture

User Input
(Text / PDF / DOCX / Screenshot)

↓

Streamlit User Interface

↓

File Processing Layer

↓

PII Processing Layer

↓

Workflow Orchestrator

↓

UI Analysis Agent

↓

Impact Analysis Agent

↓

Test Case Generation Agent

↓

Critic Agent

↓

Structured Results

## Project Structure

qa-ai-copilot/

agents/

* UI Analysis Agent
* Impact Analysis Agent
* Test Case Generation Agent
* Critic Agent

services/

* OpenAI Service
* File Processing Service
* PII Processing Service

workflows/

* Workflow Orchestrator

models/

* Workflow State
* Execution Records

app/

* Streamlit Application

storage/

* Persistence Layer

config/

* Application Configuration

tests/

* Validation and Testing Utilities

## Technology Stack

* Python
* Streamlit
* OpenAI API
* PDFPlumber
* Python-Docx
* Tesseract OCR
* SQLite
* Git & GitHub

## Current Focus

The current focus is improving the platform architecture and preparing it for enterprise-style AI workflows.

Active areas of development include:

* Workflow traceability
* Evaluation framework
* Automated quality validation
* Agent orchestration improvements
* Maintainable software architecture

## Roadmap

Near-Term Goals

* Structured execution records
* Workflow metrics
* Evaluation framework
* Automated tests
* Traceability enhancements

Long-Term Vision

Build an AI-powered QA Copilot that helps teams:

* Understand requirements faster
* Analyze change impacts
* Improve test coverage
* Reduce manual effort
* Support testers and developers throughout the software development lifecycle

## Learning Journey

This project is also a hands-on learning journey into AI Engineering.

Every feature, refactor, bug fix, and architecture decision is helping me deepen my understanding of:

* Software Engineering
* Python Development
* AI Systems
* Agentic Workflows
* Testing with AI

The platform continues to evolve as I learn and build.

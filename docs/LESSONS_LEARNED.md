//docs/LESSON_LEARNED.md
# Lessons Learned

## Python

### Dataclasses
...

## Architecture

### WorkflowState Pattern
...

### Agent Pattern
...

## Git

### Package Refactoring
...
Date: 07-Jun-2026

Topic:
Execution Tracking & Observability

Learned:

1. Dataclasses can be used to model execution metadata.

2. WorkflowState can store execution history.

3. Enterprise applications need traceability.

4. IST timestamps can be generated using zoneinfo.

5. Indentation mistakes can silently break workflow logic.

6. ExecutionRecord evolved from:
   agent_name + status

   to

   agent_name + status + timestamp

7. Traceability is different from logging.

   Logging = messages

   Traceability = execution history

8. Observability helps identify slow or failing components.
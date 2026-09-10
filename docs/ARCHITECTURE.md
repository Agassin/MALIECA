# Architecture

## Direction

M.A.L.I.E.C.A. is designed as a modular personal assistant.

```text
User
  ↓
Interface (CLI / Voice / Future UI)
  ↓
Assistant Core / Orchestrator
  ├── Context & Memory
  ├── Reasoning / Planning
  ├── Tools
  └── Configuration
          ↓
External services / Local system
```

## Rules

- Keep core logic independent from interfaces.
- Tools expose small, explicit capabilities.
- Secrets stay outside Git.
- Every important capability gets tests.
- Prefer simple implementations before complex agentic behavior.

# {{PROJECT_NAME}}

> One-sentence description of what this project does and who it serves.

## Status

See [`STATE.md`](./STATE.md) for what is done, pending, and next.

## For humans getting started

1. Read [`vision/01-product.md`](./vision/01-product.md) to understand the intent
2. Read [`vision/03-architecture.md`](./vision/03-architecture.md) for the stack
3. Follow [`playbooks/setup.md`](./playbooks/setup.md) to run locally

## For AI agents

Read [`AGENTS.md`](./AGENTS.md). It is mandatory and non-optional.

## Repository layout

```
.
├── AGENTS.md          Protocol for AI agents (read first)
├── CLAUDE.md          Pointer to AGENTS.md for Claude Code
├── STATE.md           Living status — updated every session
├── README.md          This file
│
├── vision/            Target: what we want to be (changes rarely)
├── system/            Reality: what currently exists (changes with code)
├── decisions/         ADRs: one decision per file, immutable
└── playbooks/         How-to guides: setup, deploy, tests, etc.
```

## Why three folders for documentation

Each folder answers a different question and changes at a different cadence:

- `vision/` → *what do we want to be?* (rare)
- `system/` → *what exists now?* (with code)
- `STATE.md` → *where are we right now?* (every session)

This separation prevents the single most common failure mode of AI-assisted projects: documentation that blends intent, reality, and progress into one unreadable blob.

## License

{{LICENSE}}

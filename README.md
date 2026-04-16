# agent-project-template

> A minimal, opinionated starting point for software projects built collaboratively with AI agents (Claude, Codex, Cursor, etc.). Solves the single most common failure mode of AI-assisted projects: documentation that blends intent, reality, and progress into one unreadable blob.

---

## Using this as a template

This repository **is not a project** — it is the skeleton for one. When you clone it, you get an empty structure with placeholders. An AI agent reading it will interview you to fill in the blanks before writing any code.

### Start a new project from this template

```bash
git clone https://github.com/<your-user>/agent-project-template.git my-new-project
cd my-new-project
rm -rf .git
git init
git add -A
git commit -m "initial import from agent-project-template"
```

Then open the folder in Claude Code (or any agent that reads `AGENTS.md`) and say: **"let's start"**.

The agent will read [`AGENTS.md`](./AGENTS.md), see that `vision/` files are full of `{{PLACEHOLDER}}` markers, and begin interviewing you one question at a time until the project is defined enough to scaffold.

### Keep your fork in sync with template updates (optional)

If you want to receive improvements to the template later:

```bash
git remote add template https://github.com/<your-user>/agent-project-template.git
git fetch template
git cherry-pick <commit-hash>   # pick specific template improvements
```

---

## What's inside

```
.
├── AGENTS.md          Protocol for AI agents (read first — mandatory)
├── CLAUDE.md          Pointer to AGENTS.md for Claude Code auto-load
├── STATE.md           Living status — updated every session
├── README.md          This file
│
├── vision/            Target: what we want to be (changes rarely)
│   ├── 01-product.md
│   ├── 02-scope.md
│   └── 03-architecture.md
│
├── system/            Reality: what currently exists (changes with code)
│   ├── domain.md
│   ├── api.md
│   └── flows.md
│
├── decisions/         ADRs: one decision per file, immutable
│   ├── README.md
│   └── _TEMPLATE.md
│
└── playbooks/         How-to guides: setup, deploy, tests
    ├── README.md
    └── setup.md
```

## The three-layer model

Each folder answers a different question and changes at a different cadence:

| Folder | Question | Cadence |
|---|---|---|
| `vision/` | What do we want to be? | Rarely (per quarter) |
| `system/` | What exists now? | With every code change |
| `STATE.md` | Where are we right now? | Every session |

The separation is strict. `vision/` never describes existing code. `system/` never describes aspirations. `STATE.md` is the only document that talks about *now*.

## Why this matters for AI agents

Agents drift when they can't tell intent apart from reality. They invent features the user didn't ask for, or repeat work already done, or confidently describe code that doesn't exist. This template removes the ambiguity:

- **`AGENTS.md`** forces a reading order and an interview protocol.
- **`{{PLACEHOLDER}}` markers** are tripwires: an agent that sees one knows it must ask the user, not guess.
- **Immutable ADRs** in `decisions/` preserve the *why* behind choices, so agents don't relitigate settled questions.

## License

MIT — use freely, remix freely, no warranty.

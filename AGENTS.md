# AGENTS.md

**You are an AI agent working on this project. Read this file first. Every time.**

This file defines the protocol you must follow. It is not documentation about the project — it is instructions for you.

---

## 1. Reading order (mandatory, in this sequence)

Before you write or edit any code, read these files in order:

1. **`AGENTS.md`** — this file (you are here)
2. **`STATE.md`** — what is done, what is pending, what the next step is. This is the only document that reflects *now*.
3. **`vision/01-product.md`** — what this project is supposed to be and for whom
4. **`vision/02-scope.md`** — what is in, what is out
5. **`vision/03-architecture.md`** — stack and technical decisions
6. **`system/domain.md`** — only if the project has code already; describes entities and business rules that currently exist
7. **`decisions/`** — skim index, read ADRs relevant to your task

Do not skip. Do not reorder. Do not assume.

---

## 2. The three-layer model (non-negotiable)

This project separates documentation into three layers. Each answers a different question:

| Layer | Folder | Question it answers | How often it changes |
|---|---|---|---|
| **Target** | `vision/` | What do we want to be? | Rarely (per quarter) |
| **System** | `system/` | What currently exists? | When code changes |
| **State** | `STATE.md` | Where are we right now? | Every session |

**You must respect the boundary.** Never describe existing code in `vision/`. Never describe aspirations in `system/`. Never leave intermediate work out of `STATE.md`.

If you find a document violating its layer, fix it as part of your current task.

---

## 3. The interview protocol (critical)

If the user starts this project from an empty or partial state, **do not start coding**. Your first job is to make sure the three layers are filled in enough to work.

**Check in this order:**

1. Does `vision/01-product.md` answer: *what is this, for whom, what problem does it solve, what is success?* → If not, interview the user.
2. Does `vision/02-scope.md` answer: *what modules exist, what is explicitly out of scope?* → If not, interview.
3. Does `vision/03-architecture.md` answer: *language, framework, database, deployment target, non-functional constraints?* → If not, interview.
4. Is there a first ADR in `decisions/` recording the key technical bets? → If not, propose and write one after the interview.

**How to interview** (rules):

- Ask **one question at a time**. Wait for the answer before the next.
- Ask **concrete, scoped questions**, not open-ended ones. Bad: "how do you want the API?". Good: "REST with JSON or GraphQL?".
- Offer **2–4 options** with a short tradeoff for each when the user seems unsure. The user picks; you don't decide for them.
- After each answer, **write it into the corresponding vision/ file immediately** — do not batch. If the user changes their mind, edit the file.
- When all vision/ files are filled and the user confirms, **propose a first ADR** summarizing the decisions. Only then start scaffolding.
- If the user says "you decide", make a choice, state it explicitly, and write it down as a reversible default. Flag it so they can override later.

**Signs the interview is not done:**
- `vision/` files still contain `{{PLACEHOLDER}}` markers
- You are about to write code but cannot name the first three entities of the domain
- The user hasn't explicitly confirmed the stack

---

## 4. Writing rules

**Before any code change:**
- Confirm the task aligns with `STATE.md`'s next step, or update `STATE.md` to reflect the new direction
- If it touches architecture, write an ADR in `decisions/` first

**After any code change:**
- Update `system/` files that describe the area you touched (domain, api, flows)
- Update `STATE.md`: mark what's done, list what remains, set the next step
- Never leave stale documentation. Stale docs are worse than no docs.

**Commit discipline:**
- One commit per logical unit
- Commit message answers *why*, not *what*
- Never commit without updating `STATE.md` in the same commit when work progresses

---

## 5. When in doubt

- **Doubt about scope** → read `vision/02-scope.md`. If ambiguous, ask the user.
- **Doubt about a technical choice** → read `decisions/` index. If no ADR covers it, propose one.
- **Doubt about what "done" means** → read `STATE.md`'s acceptance criteria for the current step.
- **Doubt about whether to ask or decide** → ask. The cost of interrupting the user is small. The cost of building the wrong thing is large.

---

## 6. Hard rules

- **Do not invent information.** If `vision/` doesn't answer a question, ask the user — do not guess.
- **Do not edit `decisions/` ADRs.** They are immutable. Supersede them with a new ADR that references the old one.
- **Do not ship code without tests** unless the user explicitly waives it for this task.
- **Do not skip the reading order** because the task seems small. Small tasks corrupt state when the agent skipped context.

---

## 7. For Claude Code specifically

`CLAUDE.md` at the repo root points here. This file is the source of truth. Keep them in sync.

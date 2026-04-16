# 02 — Scope

> **Layer:** Target.
> **Purpose:** define what is in, what is out, and what the modules of the system are.
> **Agent rule:** a feature request that does not map to a module below must trigger a conversation with the user before being built.

---

## In scope — modules

Each module is a coherent area of functionality. Aim for 4–8 modules total. Avoid more than 10; if you need more, the project may be too big for one team or one sprint.

### Module: {{MODULE_NAME_1}}

- **What it does:** {{RESPONSIBILITY}}
- **Key capabilities:**
  - {{CAPABILITY_1}}
  - {{CAPABILITY_2}}
- **Depends on:** {{OTHER_MODULES_OR_NONE}}

### Module: {{MODULE_NAME_2}}

- **What it does:** {{RESPONSIBILITY}}
- **Key capabilities:**
  - {{CAPABILITY_1}}
- **Depends on:** {{OTHER_MODULES_OR_NONE}}

---

## Out of scope

Things that **could** fit the product but are deliberately excluded. Each item has a reason so future conversations do not re-litigate.

- **{{OUT_OF_SCOPE_ITEM_1}}** — Reason: {{WHY_NOT}}
- **{{OUT_OF_SCOPE_ITEM_2}}** — Reason: {{WHY_NOT}}

## Explicitly deferred (not out of scope, just not now)

Features that belong to the product but are scheduled for a later phase.

- **{{DEFERRED_ITEM_1}}** — Reason: {{DEFERRAL_REASON}}

---

## Scope change protocol

When a user requests something that is not in the module list:

1. Ask whether it belongs to an existing module (add as capability) or needs a new module.
2. If it conflicts with "out of scope," surface the prior reason and ask for explicit override.
3. Update this file in the same commit as the code change.

---

## Interview checklist

- Every module has a name, responsibility, and at least one capability.
- Every out-of-scope item has a reason.
- No module depends on a module that does not exist.

# 03 — Architecture

> **Layer:** Target.
> **Purpose:** declare the technical shape of the project — stack, runtime, deployment target, non-functional constraints.
> **Agent rule:** every major technical choice here must also exist as an ADR in `decisions/`. This file is the summary; ADRs are the argument.

---

## Stack

| Layer | Choice | Reason (short) | ADR |
|---|---|---|---|
| Language (backend) | {{BACKEND_LANG}} | {{WHY}} | {{ADR_LINK}} |
| Framework (backend) | {{BACKEND_FRAMEWORK}} | {{WHY}} | {{ADR_LINK}} |
| Language (frontend) | {{FRONTEND_LANG}} | {{WHY}} | {{ADR_LINK}} |
| Framework (frontend) | {{FRONTEND_FRAMEWORK}} | {{WHY}} | {{ADR_LINK}} |
| Database | {{DATABASE}} | {{WHY}} | {{ADR_LINK}} |
| Cache / queue | {{CACHE_QUEUE_OR_NONE}} | {{WHY}} | {{ADR_LINK}} |
| Auth strategy | {{AUTH}} | {{WHY}} | {{ADR_LINK}} |
| Deployment target | {{DEPLOY_TARGET}} | {{WHY}} | {{ADR_LINK}} |

_(If a row does not apply to this project, write "N/A" in the Choice column.)_

## Repository shape

High-level layout. Details of each folder live inside them.

```
{{REPO_TREE}}
```

_(Example:
```
backend/          Python + Django API
frontend/         React + Vite monorepo
infra/            Docker, CI, deployment
```
)_

## Non-functional requirements

Numbers, not adjectives. "Fast" is not an NFR; "p95 < 300ms for reads" is.

- **Performance:** {{PERF_TARGET}}
- **Availability:** {{AVAILABILITY_TARGET}}
- **Security:** {{SECURITY_BASELINE}}
- **Compliance:** {{COMPLIANCE_OR_NONE}}
- **Accessibility:** {{A11Y_TARGET}}
- **Observability:** {{OBSERVABILITY_BASELINE}}

## Constraints from the environment

Things that limit technical choices but aren't pure preferences — corporate policy, hardware, legacy systems.

- {{CONSTRAINT_1}}

---

## Interview checklist

- Every stack row has a choice and a one-line reason, OR is marked N/A.
- At least one ADR exists in `decisions/` for each non-trivial choice.
- Non-functional requirements are stated as numbers or clear yes/no criteria, not adjectives.
- Environmental constraints are listed when they exist (e.g. "corporate Windows without admin rights").

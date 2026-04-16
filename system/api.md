# system/api.md

> **Layer:** Reality.
> **Purpose:** list endpoints/interfaces that **currently exist and work**.
> **Agent rule:** prefer auto-generation (OpenAPI, GraphQL schema, tRPC types) over hand-written tables. If hand-written, every endpoint below must return a response to a real request.

---

## Preferred approach

If the project has a schema generator (drf-spectacular, FastAPI OpenAPI, NestJS Swagger, GraphQL schema SDL, tRPC), **this file should be a pointer**:

- Generated schema: `{{PATH_OR_URL}}`
- How to regenerate: `{{COMMAND}}`
- How to browse interactively: `{{URL_TO_SWAGGER_OR_GRAPHIQL}}`

That's it. Do not duplicate what the generator produces.

---

## Hand-written fallback

Only use this section if no generator exists yet. Each endpoint must be real and currently testable.

### {{RESOURCE_NAME}}

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `{{PATH}}` | {{AUTH}} | {{WHAT}} |
| POST | `{{PATH}}` | {{AUTH}} | {{WHAT}} |

---

## Non-HTTP interfaces

If the project also exposes CLI commands, background jobs, or event consumers, list them here.

- **{{INTERFACE_NAME}}** — {{PURPOSE}}, defined in `{{PATH}}`

---

## Empty state

_(If no API exists yet, write "No API implemented." and delete the sections above.)_

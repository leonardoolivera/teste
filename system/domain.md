# system/domain.md

> **Layer:** Reality.
> **Purpose:** describe the entities and business rules that **currently exist in the code**.
> **Agent rule:** this file is a mirror of the code. If the code changes, this file changes in the same commit. If this file describes something that is not in the code, delete it.

---

## Entities

_(List in order of importance. Each entity gets a short block. No aspirations here — only what is implemented.)_

### {{ENTITY_1}}

- **Purpose:** {{ONE_LINE}}
- **Key fields:** {{FIELD_1}}, {{FIELD_2}}, {{FIELD_3}}
- **Relationships:** {{RELATIONSHIP_DESCRIPTION}}
- **File:** `{{PATH_TO_MODEL_FILE}}`

### {{ENTITY_2}}

- **Purpose:** {{ONE_LINE}}
- **Key fields:** {{FIELDS}}
- **Relationships:** {{RELATIONSHIP_DESCRIPTION}}
- **File:** `{{PATH_TO_MODEL_FILE}}`

---

## Business rules that live in code

Rules enforced by the system right now. If a rule is planned but not implemented, it does not belong here — put it in `vision/02-scope.md` under the relevant module.

- {{RULE_1}} — _enforced in `{{PATH}}`_
- {{RULE_2}} — _enforced in `{{PATH}}`_

---

## Data lifecycle

For entities that have non-trivial state transitions, document the state machine.

### {{ENTITY_WITH_STATES}}

States: `{{STATE_1}}` → `{{STATE_2}}` → `{{STATE_3}}`

Transitions:
- `{{FROM}}` → `{{TO}}`: trigger is {{EVENT}}, enforced in `{{PATH}}`

---

## Empty state

_(If the project has no domain code yet, write "No entities implemented. See `vision/02-scope.md` for planned modules." and delete the sections above.)_

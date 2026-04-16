# system/flows.md

> **Layer:** Reality.
> **Purpose:** document user-facing and automated flows that **currently work end-to-end**.
> **Agent rule:** if a flow is documented here, it must be exercised by at least one automated test. If it is not tested, it is not a flow — it is wishful thinking. Either add the test or remove the flow.

---

## User flows

A user flow is a sequence of steps a real person takes through the system, with a concrete outcome.

### Flow: {{FLOW_NAME}}

- **Actor:** {{WHO}}
- **Trigger:** {{WHAT_STARTS_IT}}
- **Steps:**
  1. {{STEP_1}}
  2. {{STEP_2}}
  3. {{STEP_3}}
- **Outcome:** {{WHAT_CHANGES_IN_THE_SYSTEM}}
- **Covered by test:** `{{PATH_TO_TEST}}`

---

## Automated flows (cron, workers, event handlers)

Anything that runs without a human initiating it.

### Flow: {{AUTOMATED_FLOW_NAME}}

- **Trigger:** {{CRON_SCHEDULE_OR_EVENT}}
- **What it does:** {{DESCRIPTION}}
- **Side effects:** {{EMAILS_SENT_DB_UPDATES_ETC}}
- **Defined in:** `{{PATH_TO_CODE}}`
- **Covered by test:** `{{PATH_TO_TEST}}`

---

## Empty state

_(If no flows are implemented end-to-end yet, write "No flows implemented." and delete the sections above.)_

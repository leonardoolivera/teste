# playbooks/

Step-by-step guides for operational tasks. Written so a new person (or agent) can follow them literally and succeed.

## What belongs here

- `setup.md` — how to get the project running locally from a fresh clone
- `deploy.md` — how to deploy (staging, prod)
- `testing.md` — how to run tests, lint, typecheck
- `troubleshooting.md` — common errors and fixes

Add playbooks only when a task is **repeated by more than one person** or **done more than once by the same person**. Do not write a playbook for a one-off.

## Rules

1. **Commands must be copy-pasteable.** No pseudo-code, no placeholders the reader has to figure out.
2. **Prerequisites go at the top.** Do not assume.
3. **Every playbook is tested by running it on a clean machine before merge.** If you cannot test it, mark it `# DRAFT — untested` at the top.
4. **When a command or path changes in the code, update the playbook in the same commit.**

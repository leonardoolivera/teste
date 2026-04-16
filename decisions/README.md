# decisions/

Architecture Decision Records. One decision per file. Immutable once committed.

## Format

`NNNN-short-slug.md` — sequential number, lowercase, dash-separated.

Examples:
- `0001-use-django-over-fastapi.md`
- `0002-postgres-not-mongo.md`
- `0003-token-auth-not-jwt.md`

## Rules

1. **Never edit an ADR after it is merged.** If a decision is revisited, write a new ADR that supersedes it, and mark the old one as superseded at the top.
2. **One decision per file.** If you're bundling two decisions, split them.
3. **Keep ADRs short.** One page is usually too long. Half a page is often right.
4. **Write the ADR before or during the change, not after.** An ADR written weeks later is a rationalization.

## Template

See [`_TEMPLATE.md`](./_TEMPLATE.md). Copy it, renumber, rename.

## Index

_(Keep this list sorted and up to date. One line per ADR.)_

- {{NO_ADRS_YET_REMOVE_THIS_LINE_WHEN_YOU_ADD_THE_FIRST}}

# CHECKLIST.md - AH.3

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2023h2-regime-atr-100/`.

## Invariantes

- [x] ADR-0019.

## Finding

SOL 2023-H2: hit 54.69% marginal, fe 10122 (+1.22%). Regime 2023 é net-wash — nem ganha nem perde materialmente.

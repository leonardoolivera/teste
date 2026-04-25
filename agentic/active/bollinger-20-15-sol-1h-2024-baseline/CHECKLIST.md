# CHECKLIST.md - AE.4

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2024-baseline/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10403.48).

## Finding

controle SOL sem filtro: hit 64.96% fe 10872 — 20/1.5 supera 20/2 em SOL 2024 mesmo sem filtro (comparar R.1 sem filtro J.1=10684)

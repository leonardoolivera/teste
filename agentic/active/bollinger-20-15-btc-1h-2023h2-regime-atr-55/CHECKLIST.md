# CHECKLIST.md - AH.2

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2023h2-regime-atr-55/`.

## Invariantes

- [x] ADR-0019.

## Finding

BTC 2023-H2 marginal: hit 58.82% OK mas fe só 10027 (+0.27%). Regime 2023 diferente de 2024-2025.

# CHECKLIST.md - AG.3

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-sol-1h-2024h1-regime-atr-100/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9584.44).

## Finding

SOL 2024-H1 marginal: hit 58% fe 9919. Cross-window SOL: 58/66/58/47% — 2024-H2 foi outlier. SOL não deve operar.

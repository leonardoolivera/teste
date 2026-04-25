# CHECKLIST.md - AG.2

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2024h1-regime-atr-55/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9662.34).

## Finding

BTC 2024-H1 marginal: hit 55.7% OK mas fe < 10000. Cross-window BTC: 55/72/58/44% — 2024-H2 foi outlier positivo, não regra.

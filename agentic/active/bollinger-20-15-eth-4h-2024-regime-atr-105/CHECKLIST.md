# CHECKLIST.md - AH.4

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-eth-4h-2024-regime-atr-105/`.

## Invariantes

- [x] ADR-0019.

## Finding

ETH 4h FALHA: fe 9478 (-5.2% capital). Edge não transfere cross-timeframe. Config 20/1.5+atr:105 é 1h-específica em ETH.

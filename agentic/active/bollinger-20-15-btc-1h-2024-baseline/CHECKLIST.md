# CHECKLIST.md - AE.3

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2024-baseline/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 9754.93).

## Finding

controle BTC sem filtro: hit 65.09% fe 10178 — 20/1.5 tem edge próprio em BTC 2024 (comparar com AE.1 para isolar ganho do filtro: +7.5pp hit, +296 fe)

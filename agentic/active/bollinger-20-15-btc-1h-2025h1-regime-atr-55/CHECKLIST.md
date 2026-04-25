# CHECKLIST.md - AF.1

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only`

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-15-btc-1h-2025h1-regime-atr-55/`.

## Invariantes

- [x] ADR-0019 (fee+10 ≡ spread+10 = 10092.02).

## Finding

BTC 2025-H1 PRESERVA edge (hit 58% fe 10360). 2025-H2 degrada (hit 44%). Decay gradual cross-window.

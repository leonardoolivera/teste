# CHECKLIST.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (41º piloto; **dominado por N.2 raw**,
filtro ATR não agrega cross-family para RSI).

- [x] pesquisa (SPEC.md)
- [x] implementação (IMPLEMENTATION.md)
- [x] validação (VALIDATION.md)
- [x] backtest (BACKTEST.md)
- [x] auditoria (AUDIT.md)

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-14-30-70-btc-1h-2024-regime-atr/`.
- [x] Dataset H.1/N.2 reusado (BTC 1h 2024-H2).

## Invariantes

- [x] ADR-0019 41ª confirmação (`fee+10 ≡ spread+10 = 9877.57`,
  stress < 10000).
- [x] ADR-0022 neutrality/lookahead/monotonicity.
- [x] ADR-0027 RSI SMA-smoothed causal.

## Ranking

Esperado abaixo de N.2 no N=41 (edge marginal, ratio não compensa
perda de hit/fe).

## Série S — encerramento

Cross-family transfer refutado. Filtro ATR é Bollinger-specific.

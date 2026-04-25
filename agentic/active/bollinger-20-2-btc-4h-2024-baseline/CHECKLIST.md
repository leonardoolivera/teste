# CHECKLIST.md — M.2 Bollinger 20/2 BTC 4h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (5º `fail` operacional; replica M.1).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-4h-2024-baseline/`.
- [x] Dataset `btcusdt_4h_20240705_20241231_binance_spot` (sha256=`2b1256ea`, 1080 barras, 0 gaps).

## Invariantes

- [x] ADR-0019 27ª confirmação (`fee+10 ≡ spread+10 = 9856.70`).
- [x] ADR-0010 monotonicity.

## Release

- [x] `fail` — hipótese SPEC violada marginalmente (9932.49 < 10000).
- [x] Critério 3 passa (0.9924): cross-asset replication de M.1.
- [ ] M.3 ETH pendente para fechar trio M.

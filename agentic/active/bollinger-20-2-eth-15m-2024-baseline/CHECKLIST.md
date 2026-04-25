# CHECKLIST.md — L.3 Bollinger 20/2 ETH 15m 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (terceiro `fail` consecutivo; fecha Série L 3/3).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-eth-15m-2024-baseline/`.
- [x] Dataset `ethusdt_15m_20240705_20241231_binance_spot` (sha256=`324086d8`).

## Invariantes

- [x] ADR-0019 25ª confirmação (`fee+10 ≡ spread+10 = 8357.51`).
- [x] ADR-0010 monotonicity.

## Release

- [x] `fail` registrado — critério 3 violado (0.855 < 0.95) + fe baseline < capital.
- [x] Série L completa 3/3 `fail`: migração 15m refutada com evidência cross-asset.
- [ ] Handoff permanece J.2 BTC 1h ou J.1 SOL 1h. Série M pendente.

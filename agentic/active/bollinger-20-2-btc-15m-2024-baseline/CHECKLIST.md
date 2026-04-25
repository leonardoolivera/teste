# CHECKLIST.md — L.2 Bollinger 20/2 BTC 15m 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (segundo `fail` consecutivo; replica L.1).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-btc-15m-2024-baseline/`.
- [x] Dataset `btcusdt_15m_20240705_20241231_binance_spot` (sha256=`8ccce65c`).

## Invariantes

- [x] ADR-0019 24ª confirmação (`fee+10 ≡ spread+10 = 8376.61`).
- [x] ADR-0010 monotonicity.

## Release

- [x] `fail` registrado — critério 3 de ADR-0025 violado (0.864 < 0.95) + fe baseline < capital.
- [ ] Não candidato a handoff. Migração 15m refutada em 2 de 2 assets.
- [ ] L.3 ETH pendente para fechar trio.

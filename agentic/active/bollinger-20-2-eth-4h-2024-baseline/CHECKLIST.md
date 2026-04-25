# CHECKLIST.md — M.3 Bollinger 20/2 ETH 4h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (6º `fail` operacional; fecha Série M 3/3).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-eth-4h-2024-baseline/`.
- [x] Dataset `ethusdt_4h_20240705_20241231_binance_spot` (sha256=`960919b7`, 1080 barras, 0 gaps).

## Invariantes

- [x] ADR-0019 28ª confirmação (`fee+10 ≡ spread+10 = 9264.56`).
- [x] ADR-0010 monotonicity.

## Release

- [x] `fail` — único da Série M com critério 1 violado (hit=43.75% < 45%) + hipótese SPEC.
- [x] Série M completa 3/3 `fail`: sweet spot 1h formalmente delimitado por L (15m) + M (4h).
- [ ] Séries N (RSI) ou O (regime filter) são próximos candidatos.

# CHECKLIST.md — M.1 Bollinger 20/2 SOL 4h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: fail` (4º `fail` operacional; trade-off oposto de L).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/bollinger-20-2-sol-4h-2024-baseline/`.
- [x] Dataset `solusdt_4h_20240705_20241231_binance_spot` (sha256=`04a5a335`, 1080 barras, 0 gaps).

## Invariantes

- [x] ADR-0019 26ª confirmação (`fee+10 ≡ spread+10 = 9683.54`).
- [x] ADR-0010 monotonicity.

## Release

- [x] `fail` registrado — hipótese SPEC violada (fe baseline < capital) + fold min hit=0%.
- [x] Critério 3 passa folgado (0.9915): simetria formal com Série L.
- [ ] M.2 BTC 4h + M.3 ETH 4h pendentes para fechar trio.
- [ ] Handoff permanece J.2 BTC 1h / J.1 SOL 1h.

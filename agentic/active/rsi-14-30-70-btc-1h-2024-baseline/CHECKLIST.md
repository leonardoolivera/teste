# CHECKLIST.md — N.2 RSI 14/30/70 BTC 1h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (30º piloto do protocolo; segundo RSI).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-14-30-70-btc-1h-2024-baseline/`.
- [x] Dataset 2024-H2 reusado (`btcusdt_1h_20240705_20241231_binance_spot`).

## Invariantes

- [x] ADR-0019 30ª confirmação (`fee+10 ≡ spread+10 = 9862.02`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0027 causalidade.

## Ranking

Elegível; melhor RSI do trio em hit/fe; candidato secundário a handoff após
sweep de parâmetros.

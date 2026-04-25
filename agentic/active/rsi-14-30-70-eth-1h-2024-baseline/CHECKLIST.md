# CHECKLIST.md — N.3 RSI 14/30/70 ETH 1h 2024

## Gates (pesquisa → implementação → validação → backtest → auditoria)

`release_decision: canary_only` (31º piloto; **fecha Série N 3/3**).

## Artefatos

- [x] 6 .md.
- [x] 4 .json em `results/validation/rsi-14-30-70-eth-1h-2024-baseline/`.
- [x] Dataset 2024-H2 reusado (`ethusdt_1h_20240705_20241231_binance_spot`).

## Invariantes

- [x] ADR-0019 31ª confirmação (`fee+10 ≡ spread+10 = 9600.61`).
- [x] ADR-0010 monotonicity.
- [x] ADR-0027 causalidade.

## Ranking

Elegível; maior hit do trio N (69.33%).

## Série N — consolidação

- 3/3 canary_only. **Edge MR @ 1h é estrutural cross-família**
  (Bollinger ∪ RSI, 6 pilotos, 6 passes).

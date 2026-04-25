# VALIDATION.md - AZ.1

## Dataset

ethusdt_1h_20240105_20240704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014, ADR-0019)
- Property: BW lookahead + monotonicity (herdados AK)

## Conformidade

- ADR-0019: fee+10 == spread+10 (fee_fe=10203.32, spread_fe=10203.32, equal=True).
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 63.64% >= 45%.

## Metricas

- trades: 0
- hit_rate (avg folds): 63.64%
- max_drawdown p95 (MC): 3.28%
- MC p5: 10053.13
- MC p50: 10577.35
- MC p95: 11172.00
- baseline fe: 10386.03
- ratio_min (fee+10/baseline): 0.9824

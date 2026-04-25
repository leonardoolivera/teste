# VALIDATION.md - AZ.4

## Dataset

solusdt_1h_20240705_20241231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014, ADR-0019)
- Property: BW lookahead + monotonicity (herdados AK)

## Conformidade

- ADR-0019: fee+10 == spread+10 (fee_fe=10364.81, spread_fe=10364.81, equal=True).
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 71.77% >= 45%.

## Metricas

- trades: 0
- hit_rate (avg folds): 71.77%
- max_drawdown p95 (MC): 4.45%
- MC p5: 10296.67
- MC p50: 10927.86
- MC p95: 11493.64
- baseline fe: 10689.86
- ratio_min (fee+10/baseline): 0.9696

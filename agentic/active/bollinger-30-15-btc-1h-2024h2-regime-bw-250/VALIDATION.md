# VALIDATION.md - AZ.2

## Dataset

btcusdt_1h_20240705_20241231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014, ADR-0019)
- Property: BW lookahead + monotonicity (herdados AK)

## Conformidade

- ADR-0019: fee+10 == spread+10 (fee_fe=10054.47, spread_fe=10054.47, equal=True).
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 73.08% >= 45%.

## Metricas

- trades: 0
- hit_rate (avg folds): 73.08%
- max_drawdown p95 (MC): 1.76%
- MC p5: 10064.02
- MC p50: 10296.37
- MC p95: 10494.37
- baseline fe: 10238.76
- ratio_min (fee+10/baseline): 0.9820

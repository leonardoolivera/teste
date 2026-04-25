# VALIDATION.md - AZ.3

## Dataset

btcusdt_1h_20250105_20250704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014, ADR-0019)
- Property: BW lookahead + monotonicity (herdados AK)

## Conformidade

- ADR-0019: fee+10 == spread+10 (fee_fe=10229.99, spread_fe=10229.99, equal=True).
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 62.50% >= 45%.

## Metricas

- trades: 0
- hit_rate (avg folds): 62.50%
- max_drawdown p95 (MC): 0.48%
- MC p5: 10151.27
- MC p50: 10329.71
- MC p95: 10511.91
- baseline fe: 10370.58
- ratio_min (fee+10/baseline): 0.9864

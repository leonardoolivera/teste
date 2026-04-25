# VALIDATION.md - AK.5

## Dataset

ethusdt_1h_20240105_20240704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)
- Property: lookahead + monotonicity (ADR-0022)

## Conformidade

- ADR-0019: bit-identico.
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 63.16% >= 45%.

## Metricas

- trades: 38
- hit_rate: 63.16%
- max_drawdown: 3.45%
- final_equity: 10162.87
- MC p5: 9669.64
- ratio_min: 0.9848

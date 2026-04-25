# VALIDATION.md - AK.2

## Dataset

ethusdt_1h_20240705_20241231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)
- Property: lookahead + monotonicity (ADR-0022)

## Conformidade

- ADR-0019: bit-identico.
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 71.79% >= 45%.

## Metricas

- trades: 78
- hit_rate: 71.79%
- max_drawdown: 3.47%
- final_equity: 10638.69
- MC p5: 9827.14
- ratio_min: 0.9706

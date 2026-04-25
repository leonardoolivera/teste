# VALIDATION.md - AK.6

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
- ADR-0025: hit 71.43% >= 45%.

## Metricas

- trades: 42
- hit_rate: 71.43%
- max_drawdown: 1.93%
- final_equity: 10623.18
- MC p5: 10169.75
- ratio_min: 0.9841

# VALIDATION.md - AK.8

## Dataset

ethusdt_1h_20250705_20251231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)
- Property: lookahead + monotonicity (ADR-0022)

## Conformidade

- ADR-0019: bit-identico.
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 68.75% >= 45%.

## Metricas

- trades: 48
- hit_rate: 68.75%
- max_drawdown: 3.15%
- final_equity: 10222.22
- MC p5: 9571.47
- ratio_min: 0.9812

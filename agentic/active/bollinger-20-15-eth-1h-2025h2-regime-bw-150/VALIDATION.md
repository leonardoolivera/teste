# VALIDATION.md - AK.4

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
- ADR-0025: hit 58.75% >= 45%.

## Metricas

- trades: 80
- hit_rate: 58.75%
- max_drawdown: 4.40%
- final_equity: 10151.44
- MC p5: 9336.27
- ratio_min: 0.9685

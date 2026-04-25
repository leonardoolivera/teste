# VALIDATION.md - AJ.6

## Dataset

ethusdt_1h_20250705_20251231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 60.61% >= 45%.

## Metricas

- trades: 33
- hit_rate: 60.61%
- max_drawdown: 3.51%
- final_equity: 10053.74
- MC p5: 9513.14
- ratio_min: 0.9869

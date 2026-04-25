# VALIDATION.md - AJ.3

## Dataset

ethusdt_1h_20250705_20251231_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 61.43% >= 45%.

## Metricas

- trades: 70
- hit_rate: 61.43%
- max_drawdown: 3.32%
- final_equity: 10215.46
- MC p5: 9459.67
- ratio_min: 0.9726

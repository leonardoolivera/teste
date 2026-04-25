# VALIDATION.md - AJ.2

## Dataset

ethusdt_1h_20250105_20250704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 65.33% >= 45%.

## Metricas

- trades: 75
- hit_rate: 65.33%
- max_drawdown: 5.72%
- final_equity: 10410.32
- MC p5: 9776.86
- ratio_min: 0.9711

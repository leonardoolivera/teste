# VALIDATION.md - AJ.1

## Dataset

ethusdt_1h_20240105_20240704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 64.91% >= 45%.

## Metricas

- trades: 57
- hit_rate: 64.91%
- max_drawdown: 3.00%
- final_equity: 10409.76
- MC p5: 10104.77
- ratio_min: 0.9778

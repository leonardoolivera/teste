# VALIDATION.md - AJ.5

## Dataset

ethusdt_1h_20250105_20250704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 60.87% >= 45%.

## Metricas

- trades: 46
- hit_rate: 60.87%
- max_drawdown: 3.09%
- final_equity: 10381.86
- MC p5: 9627.76
- ratio_min: 0.9822

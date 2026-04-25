# VALIDATION.md - AJ.4

## Dataset

ethusdt_1h_20240105_20240704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019: fee+delta=spread+delta bit-identico.
- ADR-0022/0023: regime filter OK.
- ADR-0025: hit 76.92% >= 45%.

## Metricas

- trades: 26
- hit_rate: 76.92%
- max_drawdown: 1.78%
- final_equity: 10654.73
- MC p5: 10266.84
- ratio_min: 0.9901

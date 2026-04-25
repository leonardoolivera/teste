# VALIDATION.md - AI.3

## Dataset

ethusdt_1h_20240705_20241231_binance_spot (4368 barras, zero gaps).

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019 fee+delta=spread+delta: bit-identico.
- ADR-0022/0023: regime filter contract OK.
- ADR-0025: hit 70.37% >= 45%.

## Metricas

- trades: 54
- hit_rate: 70.37%
- max_drawdown: 3.59%
- final_equity: 10666.52
- MC p5: 10084.01
- ratio_min stress: 0.9796

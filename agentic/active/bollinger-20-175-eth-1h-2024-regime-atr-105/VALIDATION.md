# VALIDATION.md - AI.2

## Dataset

ethusdt_1h_20240705_20241231_binance_spot (4368 barras, zero gaps).

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019 fee+delta=spread+delta: bit-identico.
- ADR-0022/0023: regime filter contract OK.
- ADR-0025: hit 66.67% >= 45%.

## Metricas

- trades: 39
- hit_rate: 66.67%
- max_drawdown: 3.41%
- final_equity: 10592.56
- MC p5: 10094.38
- ratio_min stress: 0.9852

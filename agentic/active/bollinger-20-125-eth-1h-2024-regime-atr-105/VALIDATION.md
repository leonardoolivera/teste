# VALIDATION.md - AI.1

## Dataset

ethusdt_1h_20240705_20241231_binance_spot (4368 barras, zero gaps).

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)

## Conformidade

- ADR-0019 fee+delta=spread+delta: bit-identico.
- ADR-0022/0023: regime filter contract OK.
- ADR-0025: hit 60.47% >= 45%.

## Metricas

- trades: 43
- hit_rate: 60.47%
- max_drawdown: 3.05%
- final_equity: 10359.60
- MC p5: 10098.03
- ratio_min stress: 0.9833

# VALIDATION.md - AK.3

## Dataset

ethusdt_1h_20250105_20250704_binance_spot.

## Testes executados

- Walk-forward 4 folds (ADR-0003)
- Monte Carlo 1000 resamples seed=42
- Cost stress fee+10 / spread+10 (ADR-0014)
- Property: lookahead + monotonicity (ADR-0022)

## Conformidade

- ADR-0019: bit-identico.
- ADR-0022: contrato RegimeFilter OK.
- ADR-0025: hit 66.33% >= 45%.

## Metricas

- trades: 98
- hit_rate: 66.33%
- max_drawdown: 4.91%
- final_equity: 10440.49
- MC p5: 9654.61
- ratio_min: 0.9622

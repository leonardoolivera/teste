# VALIDATION.md - AK.7

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
- ADR-0025: hit 60.94% >= 45%.

## Metricas

- trades: 64
- hit_rate: 60.94%
- max_drawdown: 4.60%
- final_equity: 10516.34
- MC p5: 10061.32
- ratio_min: 0.9754

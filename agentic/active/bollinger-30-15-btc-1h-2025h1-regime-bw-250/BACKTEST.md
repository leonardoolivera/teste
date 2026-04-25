# BACKTEST.md - AZ.3

## Dataset

btcusdt_1h_20250105_20250704_binance_spot.

## Metricas

- MC p5: 10151.27
- MC p50: 10329.71
- MC p95: 10511.91
- hit_rate (avg folds): 62.50%
- trades: 0
- mdd p95 (MC): 0.48%
- baseline_fe: 10370.58
- ratio_min: 0.9864

## Stress

fee+10 / spread+10: fee_fe=10229.99, spread_fe=10229.99, bit-identico=True (ADR-0019).

## Strict tail gate

p5 >= 10000: PASS
mdd p95 <= 10%: PASS
ratio >= 0.95: PASS
fee==spread: PASS

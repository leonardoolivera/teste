# BACKTEST.md - AZ.4

## Dataset

solusdt_1h_20240705_20241231_binance_spot.

## Metricas

- MC p5: 10296.67
- MC p50: 10927.86
- MC p95: 11493.64
- hit_rate (avg folds): 71.77%
- trades: 0
- mdd p95 (MC): 4.45%
- baseline_fe: 10689.86
- ratio_min: 0.9696

## Stress

fee+10 / spread+10: fee_fe=10364.81, spread_fe=10364.81, bit-identico=True (ADR-0019).

## Strict tail gate

p5 >= 10000: PASS
mdd p95 <= 10%: PASS
ratio >= 0.95: PASS
fee==spread: PASS

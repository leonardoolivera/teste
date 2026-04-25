# BACKTEST.md - AZ.2

## Dataset

btcusdt_1h_20240705_20241231_binance_spot.

## Metricas

- MC p5: 10064.02
- MC p50: 10296.37
- MC p95: 10494.37
- hit_rate (avg folds): 73.08%
- trades: 0
- mdd p95 (MC): 1.76%
- baseline_fe: 10238.76
- ratio_min: 0.9820

## Stress

fee+10 / spread+10: fee_fe=10054.47, spread_fe=10054.47, bit-identico=True (ADR-0019).

## Strict tail gate

p5 >= 10000: PASS
mdd p95 <= 10%: PASS
ratio >= 0.95: PASS
fee==spread: PASS

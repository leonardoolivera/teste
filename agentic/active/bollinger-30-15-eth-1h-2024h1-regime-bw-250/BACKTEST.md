# BACKTEST.md - AZ.1

## Dataset

ethusdt_1h_20240105_20240704_binance_spot.

## Metricas

- MC p5: 10053.13
- MC p50: 10577.35
- MC p95: 11172.00
- hit_rate (avg folds): 63.64%
- trades: 0
- mdd p95 (MC): 3.28%
- baseline_fe: 10386.03
- ratio_min: 0.9824

## Stress

fee+10 / spread+10: fee_fe=10203.32, spread_fe=10203.32, bit-identico=True (ADR-0019).

## Strict tail gate

p5 >= 10000: PASS
mdd p95 <= 10%: PASS
ratio >= 0.95: PASS
fee==spread: PASS

# Roadmap 1000 estratégias — TF10m exaustão + backlog

**Date:** 2026-04-21
**Status:** Draft
**Total entries:** 1000

## Priority tiers

- **Tier 1** (~250): high-EV extensions de achados atuais (Padrão 50 cross-era, Padrão 48 regime SOL, portfolio stack13, param sensitivity stack, regime detection meta).
- **Tier 2** (~300): param grid sweeps engines stack canonical 1h (BB, RSI, composite, filter combos).
- **Tier 3** (~300): coverage gaps (TFs non-MR, short variants, Keltner/zscore reabertura restritiva, asset expansion LINK/DOT/AVAX).
- **Tier 4** (~150): long tail (stress adversarial, ablation, exotic signals requer código novo).

## Execução

Executar por **Fase** (bloco de 20-30 probes relacionadas), não por probe isolado. ~10min/probe → 1000 probes ≈ 170h compute (serial), ~5 semanas 24/7 ou distribuído.

Recomendação: processar tier 1 primeiro (250 probes ≈ 42h) antes de mover para tier 2+.

## Tabela completa

| # | Tier | ID | Engine | Dir | TF | Asset | Window | Filter | Params | Prior | Rationale |
|---:|---:|---|---|---|---|---|---|---|---|---:|---|
| 1 | T1 | T1-RM-BTC-2024-H2-atr_expansion_50pct | regime_meta | adaptive | mix | BTC | 2024-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 2 | T1 | T1-RM-BTC-2024-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | BTC | 2024-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 3 | T1 | T1-RM-BTC-2024-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | BTC | 2024-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 4 | T1 | T1-RM-BTC-2024-H2-width_narrow_10m | regime_meta | adaptive | mix | BTC | 2024-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 5 | T1 | T1-RM-BTC-2024-H2-funding_rate_extreme | regime_meta | adaptive | mix | BTC | 2024-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 6 | T1 | T1-RM-BTC-2025-H1-atr_expansion_50pct | regime_meta | adaptive | mix | BTC | 2025-H1 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 7 | T1 | T1-RM-BTC-2025-H1-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | BTC | 2025-H1 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 8 | T1 | T1-RM-BTC-2025-H1-realized_vol_percentile_70 | regime_meta | adaptive | mix | BTC | 2025-H1 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 9 | T1 | T1-RM-BTC-2025-H1-width_narrow_10m | regime_meta | adaptive | mix | BTC | 2025-H1 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 10 | T1 | T1-RM-BTC-2025-H1-funding_rate_extreme | regime_meta | adaptive | mix | BTC | 2025-H1 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 11 | T1 | T1-RM-BTC-2025-H2-atr_expansion_50pct | regime_meta | adaptive | mix | BTC | 2025-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 12 | T1 | T1-RM-BTC-2025-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | BTC | 2025-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 13 | T1 | T1-RM-BTC-2025-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | BTC | 2025-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 14 | T1 | T1-RM-BTC-2025-H2-width_narrow_10m | regime_meta | adaptive | mix | BTC | 2025-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 15 | T1 | T1-RM-BTC-2025-H2-funding_rate_extreme | regime_meta | adaptive | mix | BTC | 2025-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 16 | T1 | T1-RM-ETH-2024-H2-atr_expansion_50pct | regime_meta | adaptive | mix | ETH | 2024-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 17 | T1 | T1-RM-ETH-2024-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | ETH | 2024-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 18 | T1 | T1-RM-ETH-2024-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | ETH | 2024-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 19 | T1 | T1-RM-ETH-2024-H2-width_narrow_10m | regime_meta | adaptive | mix | ETH | 2024-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 20 | T1 | T1-RM-ETH-2024-H2-funding_rate_extreme | regime_meta | adaptive | mix | ETH | 2024-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 21 | T1 | T1-RM-ETH-2025-H1-atr_expansion_50pct | regime_meta | adaptive | mix | ETH | 2025-H1 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 22 | T1 | T1-RM-ETH-2025-H1-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | ETH | 2025-H1 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 23 | T1 | T1-RM-ETH-2025-H1-realized_vol_percentile_70 | regime_meta | adaptive | mix | ETH | 2025-H1 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 24 | T1 | T1-RM-ETH-2025-H1-width_narrow_10m | regime_meta | adaptive | mix | ETH | 2025-H1 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 25 | T1 | T1-RM-ETH-2025-H1-funding_rate_extreme | regime_meta | adaptive | mix | ETH | 2025-H1 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 26 | T1 | T1-RM-ETH-2025-H2-atr_expansion_50pct | regime_meta | adaptive | mix | ETH | 2025-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 27 | T1 | T1-RM-ETH-2025-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | ETH | 2025-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 28 | T1 | T1-RM-ETH-2025-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | ETH | 2025-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 29 | T1 | T1-RM-ETH-2025-H2-width_narrow_10m | regime_meta | adaptive | mix | ETH | 2025-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 30 | T1 | T1-RM-ETH-2025-H2-funding_rate_extreme | regime_meta | adaptive | mix | ETH | 2025-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 31 | T1 | T1-RM-SOL-2024-H2-atr_expansion_50pct | regime_meta | adaptive | mix | SOL | 2024-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 32 | T1 | T1-RM-SOL-2024-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | SOL | 2024-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 33 | T1 | T1-RM-SOL-2024-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | SOL | 2024-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 34 | T1 | T1-RM-SOL-2024-H2-width_narrow_10m | regime_meta | adaptive | mix | SOL | 2024-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 35 | T1 | T1-RM-SOL-2024-H2-funding_rate_extreme | regime_meta | adaptive | mix | SOL | 2024-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 36 | T1 | T1-RM-SOL-2025-H1-atr_expansion_50pct | regime_meta | adaptive | mix | SOL | 2025-H1 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 37 | T1 | T1-RM-SOL-2025-H1-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | SOL | 2025-H1 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 38 | T1 | T1-RM-SOL-2025-H1-realized_vol_percentile_70 | regime_meta | adaptive | mix | SOL | 2025-H1 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 39 | T1 | T1-RM-SOL-2025-H1-width_narrow_10m | regime_meta | adaptive | mix | SOL | 2025-H1 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 40 | T1 | T1-RM-SOL-2025-H1-funding_rate_extreme | regime_meta | adaptive | mix | SOL | 2025-H1 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 41 | T1 | T1-RM-SOL-2025-H2-atr_expansion_50pct | regime_meta | adaptive | mix | SOL | 2025-H2 | atr_expansion_50pct | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 42 | T1 | T1-RM-SOL-2025-H2-trend_htf_4h_sma50_flat | regime_meta | adaptive | mix | SOL | 2025-H2 | trend_htf_4h_sma50_flat | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 43 | T1 | T1-RM-SOL-2025-H2-realized_vol_percentile_70 | regime_meta | adaptive | mix | SOL | 2025-H2 | realized_vol_percentile_70 | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 44 | T1 | T1-RM-SOL-2025-H2-width_narrow_10m | regime_meta | adaptive | mix | SOL | 2025-H2 | width_narrow_10m | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 45 | T1 | T1-RM-SOL-2025-H2-funding_rate_extreme | regime_meta | adaptive | mix | SOL | 2025-H2 | funding_rate_extreme | stack_13_gated_by_regime | 25% | regime detection baseado em Padrões 48+50 (SOL 2024-H2 MR-fr |
| 46 | T1 | T1-MA-10-30-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 47 | T1 | T1-MA-10-30-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 48 | T1 | T1-MA-10-30-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 49 | T1 | T1-MA-10-30-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 50 | T1 | T1-MA-10-30-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 51 | T1 | T1-MA-10-30-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=10,long=30 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 52 | T1 | T1-MA-15-45-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 53 | T1 | T1-MA-15-45-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 54 | T1 | T1-MA-15-45-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 55 | T1 | T1-MA-15-45-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 56 | T1 | T1-MA-15-45-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 57 | T1 | T1-MA-15-45-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=15,long=45 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 58 | T1 | T1-MA-20-50-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 59 | T1 | T1-MA-20-50-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 60 | T1 | T1-MA-20-50-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 61 | T1 | T1-MA-20-50-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 62 | T1 | T1-MA-20-50-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 63 | T1 | T1-MA-20-50-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=20,long=50 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 64 | T1 | T1-MA-25-75-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 65 | T1 | T1-MA-25-75-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 66 | T1 | T1-MA-25-75-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 67 | T1 | T1-MA-25-75-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 68 | T1 | T1-MA-25-75-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 69 | T1 | T1-MA-25-75-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=25,long=75 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 70 | T1 | T1-MA-30-90-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 71 | T1 | T1-MA-30-90-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 72 | T1 | T1-MA-30-90-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 73 | T1 | T1-MA-30-90-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 74 | T1 | T1-MA-30-90-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 75 | T1 | T1-MA-30-90-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=30,long=90 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 76 | T1 | T1-MA-50-200-ETH-2024-H2 | ma_crossover | long | 10m | ETH | 2024-H2 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 77 | T1 | T1-MA-50-200-ETH-2025-H1 | ma_crossover | long | 10m | ETH | 2025-H1 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 78 | T1 | T1-MA-50-200-ETH-2025-H2 | ma_crossover | long | 10m | ETH | 2025-H2 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 79 | T1 | T1-MA-50-200-SOL-2024-H2 | ma_crossover | long | 10m | SOL | 2024-H2 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 80 | T1 | T1-MA-50-200-SOL-2025-H1 | ma_crossover | long | 10m | SOL | 2025-H1 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 81 | T1 | T1-MA-50-200-SOL-2025-H2 | ma_crossover | long | 10m | SOL | 2025-H2 | none | short=50,long=200 | 18% | Padrão 50 cross-era MA crossover bear-avoidance |
| 82 | T1 | T1-ST-7-2.5-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 83 | T1 | T1-ST-7-2.5-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 84 | T1 | T1-ST-7-2.5-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 85 | T1 | T1-ST-7-2.5-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 86 | T1 | T1-ST-7-2.5-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 87 | T1 | T1-ST-7-2.5-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=7,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 88 | T1 | T1-ST-10-2.5-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 89 | T1 | T1-ST-10-2.5-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 90 | T1 | T1-ST-10-2.5-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 91 | T1 | T1-ST-10-2.5-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 92 | T1 | T1-ST-10-2.5-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 93 | T1 | T1-ST-10-2.5-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=10,atr_mult=2.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 94 | T1 | T1-ST-10-3.0-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 95 | T1 | T1-ST-10-3.0-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 96 | T1 | T1-ST-10-3.0-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 97 | T1 | T1-ST-10-3.0-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 98 | T1 | T1-ST-10-3.0-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 99 | T1 | T1-ST-10-3.0-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=10,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 100 | T1 | T1-ST-14-3.0-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 101 | T1 | T1-ST-14-3.0-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 102 | T1 | T1-ST-14-3.0-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 103 | T1 | T1-ST-14-3.0-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 104 | T1 | T1-ST-14-3.0-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 105 | T1 | T1-ST-14-3.0-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=14,atr_mult=3.0 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 106 | T1 | T1-ST-14-3.5-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 107 | T1 | T1-ST-14-3.5-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 108 | T1 | T1-ST-14-3.5-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 109 | T1 | T1-ST-14-3.5-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 110 | T1 | T1-ST-14-3.5-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 111 | T1 | T1-ST-14-3.5-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=14,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 112 | T1 | T1-ST-20-3.5-ETH-2024-H2 | supertrend | long | 10m | ETH | 2024-H2 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 113 | T1 | T1-ST-20-3.5-ETH-2025-H1 | supertrend | long | 10m | ETH | 2025-H1 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 114 | T1 | T1-ST-20-3.5-ETH-2025-H2 | supertrend | long | 10m | ETH | 2025-H2 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 115 | T1 | T1-ST-20-3.5-SOL-2024-H2 | supertrend | long | 10m | SOL | 2024-H2 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 116 | T1 | T1-ST-20-3.5-SOL-2025-H1 | supertrend | long | 10m | SOL | 2025-H1 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 117 | T1 | T1-ST-20-3.5-SOL-2025-H2 | supertrend | long | 10m | SOL | 2025-H2 | none | atr_period=20,atr_mult=3.5 | 18% | Padrão 50 cross-era supertrend bear-avoidance |
| 118 | T1 | T1-48-bollinger-short-SOL-2024-H2 | bollinger | short | 10m | SOL | 2024-H2 | none | window=20,num_std=2.0 | 22% | Padrão 48 SOL regime replication cross-window |
| 119 | T1 | T1-48-bollinger-short-SOL-2025-H1 | bollinger | short | 10m | SOL | 2025-H1 | none | window=20,num_std=2.0 | 8% | Padrão 48 SOL regime replication cross-window |
| 120 | T1 | T1-48-bollinger-short-SOL-2025-H2 | bollinger | short | 10m | SOL | 2025-H2 | none | window=20,num_std=2.0 | 8% | Padrão 48 SOL regime replication cross-window |
| 121 | T1 | T1-48-bollinger-long-SOL-2024-H2 | bollinger | long | 10m | SOL | 2024-H2 | none | window=30,num_std=1.5 | 22% | Padrão 48 SOL regime replication cross-window |
| 122 | T1 | T1-48-bollinger-long-SOL-2025-H1 | bollinger | long | 10m | SOL | 2025-H1 | none | window=30,num_std=1.5 | 8% | Padrão 48 SOL regime replication cross-window |
| 123 | T1 | T1-48-bollinger-long-SOL-2025-H2 | bollinger | long | 10m | SOL | 2025-H2 | none | window=30,num_std=1.5 | 8% | Padrão 48 SOL regime replication cross-window |
| 124 | T1 | T1-48-rsi-short-SOL-2024-H2 | rsi | short | 10m | SOL | 2024-H2 | none | period=14,os=30,ob=70 | 22% | Padrão 48 SOL regime replication cross-window |
| 125 | T1 | T1-48-rsi-short-SOL-2025-H1 | rsi | short | 10m | SOL | 2025-H1 | none | period=14,os=30,ob=70 | 8% | Padrão 48 SOL regime replication cross-window |
| 126 | T1 | T1-48-rsi-short-SOL-2025-H2 | rsi | short | 10m | SOL | 2025-H2 | none | period=14,os=30,ob=70 | 8% | Padrão 48 SOL regime replication cross-window |
| 127 | T1 | T1-48-rsi-long-SOL-2024-H2 | rsi | long | 10m | SOL | 2024-H2 | none | period=14,os=30,ob=70 | 22% | Padrão 48 SOL regime replication cross-window |
| 128 | T1 | T1-48-rsi-long-SOL-2025-H1 | rsi | long | 10m | SOL | 2025-H1 | none | period=14,os=30,ob=70 | 8% | Padrão 48 SOL regime replication cross-window |
| 129 | T1 | T1-48-rsi-long-SOL-2025-H2 | rsi | long | 10m | SOL | 2025-H2 | none | period=14,os=30,ob=70 | 8% | Padrão 48 SOL regime replication cross-window |
| 130 | T1 | T1-48-composite_bb_rsi-short-SOL-2024-H2 | composite_bb_rsi | short | 10m | SOL | 2024-H2 | none | bb=20/2,rsi=14/30/70 | 22% | Padrão 48 SOL regime replication cross-window |
| 131 | T1 | T1-48-composite_bb_rsi-short-SOL-2025-H1 | composite_bb_rsi | short | 10m | SOL | 2025-H1 | none | bb=20/2,rsi=14/30/70 | 8% | Padrão 48 SOL regime replication cross-window |
| 132 | T1 | T1-48-composite_bb_rsi-short-SOL-2025-H2 | composite_bb_rsi | short | 10m | SOL | 2025-H2 | none | bb=20/2,rsi=14/30/70 | 8% | Padrão 48 SOL regime replication cross-window |
| 133 | T1 | T1-48-bollinger-short-SOL-2024-H1 | bollinger | short | 10m | SOL | 2024-H1 | none | window=20,num_std=2.0 | 15% | Padrão 48 expansion SOL 2024-H1 (requires data ingest) |
| 134 | T1 | T1-48-bollinger-long-SOL-2024-H1 | bollinger | long | 10m | SOL | 2024-H1 | none | window=30,num_std=1.5 | 15% | Padrão 48 expansion SOL 2024-H1 (requires data ingest) |
| 135 | T1 | T1-48-rsi-short-SOL-2024-H1 | rsi | short | 10m | SOL | 2024-H1 | none | period=14,os=30,ob=70 | 15% | Padrão 48 expansion SOL 2024-H1 (requires data ingest) |
| 136 | T1 | T1-48-rsi-long-SOL-2024-H1 | rsi | long | 10m | SOL | 2024-H1 | none | period=14,os=30,ob=70 | 15% | Padrão 48 expansion SOL 2024-H1 (requires data ingest) |
| 137 | T1 | T1-48-composite_bb_rsi-short-SOL-2024-H1 | composite_bb_rsi | short | 10m | SOL | 2024-H1 | none | bb=20/2,rsi=14/30/70 | 15% | Padrão 48 expansion SOL 2024-H1 (requires data ingest) |
| 138 | T1 | T1-PF-equal_weight-2024-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=equal_weight,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 139 | T1 | T1-PF-equal_weight-2024-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=equal_weight,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 140 | T1 | T1-PF-equal_weight-2024-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=equal_weight,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 141 | T1 | T1-PF-equal_weight-2025-H1-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=equal_weight,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 142 | T1 | T1-PF-equal_weight-2025-H1-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=equal_weight,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 143 | T1 | T1-PF-equal_weight-2025-H1-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=equal_weight,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 144 | T1 | T1-PF-equal_weight-2025-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=equal_weight,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 145 | T1 | T1-PF-equal_weight-2025-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=equal_weight,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 146 | T1 | T1-PF-equal_weight-2025-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=equal_weight,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 147 | T1 | T1-PF-risk_parity_vol-2024-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=risk_parity_vol,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 148 | T1 | T1-PF-risk_parity_vol-2024-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=risk_parity_vol,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 149 | T1 | T1-PF-risk_parity_vol-2024-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=risk_parity_vol,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 150 | T1 | T1-PF-risk_parity_vol-2025-H1-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=risk_parity_vol,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 151 | T1 | T1-PF-risk_parity_vol-2025-H1-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=risk_parity_vol,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 152 | T1 | T1-PF-risk_parity_vol-2025-H1-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=risk_parity_vol,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 153 | T1 | T1-PF-risk_parity_vol-2025-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=risk_parity_vol,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 154 | T1 | T1-PF-risk_parity_vol-2025-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=risk_parity_vol,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 155 | T1 | T1-PF-risk_parity_vol-2025-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=risk_parity_vol,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 156 | T1 | T1-PF-sharpe_weighted-2024-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=sharpe_weighted,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 157 | T1 | T1-PF-sharpe_weighted-2024-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=sharpe_weighted,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 158 | T1 | T1-PF-sharpe_weighted-2024-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=sharpe_weighted,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 159 | T1 | T1-PF-sharpe_weighted-2025-H1-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=sharpe_weighted,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 160 | T1 | T1-PF-sharpe_weighted-2025-H1-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=sharpe_weighted,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 161 | T1 | T1-PF-sharpe_weighted-2025-H1-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=sharpe_weighted,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 162 | T1 | T1-PF-sharpe_weighted-2025-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=sharpe_weighted,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 163 | T1 | T1-PF-sharpe_weighted-2025-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=sharpe_weighted,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 164 | T1 | T1-PF-sharpe_weighted-2025-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=sharpe_weighted,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 165 | T1 | T1-PF-min_var-2024-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=min_var,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 166 | T1 | T1-PF-min_var-2024-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=min_var,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 167 | T1 | T1-PF-min_var-2024-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2024-H2 | none | alloc=min_var,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 168 | T1 | T1-PF-min_var-2025-H1-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=min_var,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 169 | T1 | T1-PF-min_var-2025-H1-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=min_var,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 170 | T1 | T1-PF-min_var-2025-H1-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H1 | none | alloc=min_var,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 171 | T1 | T1-PF-min_var-2025-H2-cw30 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=min_var,corr_window=30 | 30% | portfolio combining 13 validated stack combos |
| 172 | T1 | T1-PF-min_var-2025-H2-cw60 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=min_var,corr_window=60 | 30% | portfolio combining 13 validated stack combos |
| 173 | T1 | T1-PF-min_var-2025-H2-cw90 | portfolio_stack13 | mixed | 1h | multi | 2025-H2 | none | alloc=min_var,corr_window=90 | 30% | portfolio combining 13 validated stack combos |
| 174 | T1 | T1-PF-sub-btc_only-equal_weight-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=btc_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 175 | T1 | T1-PF-sub-btc_only-risk_parity_vol-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=btc_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 176 | T1 | T1-PF-sub-btc_only-equal_weight-2025-H1 | portfolio_subset | mixed | 1h | multi | 2025-H1 | none | subset=btc_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 177 | T1 | T1-PF-sub-btc_only-risk_parity_vol-2025-H1 | portfolio_subset | mixed | 1h | multi | 2025-H1 | none | subset=btc_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 178 | T1 | T1-PF-sub-btc_only-equal_weight-2025-H2 | portfolio_subset | mixed | 1h | multi | 2025-H2 | none | subset=btc_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 179 | T1 | T1-PF-sub-btc_only-risk_parity_vol-2025-H2 | portfolio_subset | mixed | 1h | multi | 2025-H2 | none | subset=btc_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 180 | T1 | T1-PF-sub-eth_only-equal_weight-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=eth_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 181 | T1 | T1-PF-sub-eth_only-risk_parity_vol-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=eth_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 182 | T1 | T1-PF-sub-eth_only-equal_weight-2025-H1 | portfolio_subset | mixed | 1h | multi | 2025-H1 | none | subset=eth_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 183 | T1 | T1-PF-sub-eth_only-risk_parity_vol-2025-H1 | portfolio_subset | mixed | 1h | multi | 2025-H1 | none | subset=eth_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 184 | T1 | T1-PF-sub-eth_only-equal_weight-2025-H2 | portfolio_subset | mixed | 1h | multi | 2025-H2 | none | subset=eth_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 185 | T1 | T1-PF-sub-eth_only-risk_parity_vol-2025-H2 | portfolio_subset | mixed | 1h | multi | 2025-H2 | none | subset=eth_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 186 | T1 | T1-PF-sub-sol_only-equal_weight-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=sol_only,alloc=equal_weight | 25% | portfolio subset analysis |
| 187 | T1 | T1-PF-sub-sol_only-risk_parity_vol-2024-H2 | portfolio_subset | mixed | 1h | multi | 2024-H2 | none | subset=sol_only,alloc=risk_parity_vol | 25% | portfolio subset analysis |
| 188 | T1 | T1-PS-v2_bol_long-win_up-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 189 | T1 | T1-PS-v2_bol_long-win_up-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 190 | T1 | T1-PS-v2_bol_long-win_up-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 191 | T1 | T1-PS-v2_bol_long-win_down-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 192 | T1 | T1-PS-v2_bol_long-win_down-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 193 | T1 | T1-PS-v2_bol_long-win_down-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 194 | T1 | T1-PS-v2_bol_long-ns_up-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 195 | T1 | T1-PS-v2_bol_long-ns_up-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 196 | T1 | T1-PS-v2_bol_long-ns_up-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 197 | T1 | T1-PS-v2_bol_long-ns_down-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | num_std -= 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 198 | T1 | T1-PS-v2_bol_long-ns_down-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | num_std -= 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 199 | T1 | T1-PS-v2_bol_long-ns_down-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | num_std -= 0.25 | 20% | stack v2_bol_long param sensitivity test |
| 200 | T1 | T1-PS-v2_bol_long-period_up-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | period *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 201 | T1 | T1-PS-v2_bol_long-period_up-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | period *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 202 | T1 | T1-PS-v2_bol_long-period_up-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | period *= 1.2 | 20% | stack v2_bol_long param sensitivity test |
| 203 | T1 | T1-PS-v2_bol_long-period_down-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | period *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 204 | T1 | T1-PS-v2_bol_long-period_down-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | period *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 205 | T1 | T1-PS-v2_bol_long-period_down-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | period *= 0.83 | 20% | stack v2_bol_long param sensitivity test |
| 206 | T1 | T1-PS-v2_bol_long-threshold_tight-BTC | bollinger | long | 1h | BTC | 2024-H2 | stack_canonical | threshold ± 5 | 20% | stack v2_bol_long param sensitivity test |
| 207 | T1 | T1-PS-v2_bol_long-threshold_tight-ETH | bollinger | long | 1h | ETH | 2024-H2 | stack_canonical | threshold ± 5 | 20% | stack v2_bol_long param sensitivity test |
| 208 | T1 | T1-PS-v2_bol_long-threshold_tight-SOL | bollinger | long | 1h | SOL | 2024-H2 | stack_canonical | threshold ± 5 | 20% | stack v2_bol_long param sensitivity test |
| 209 | T1 | T1-PS-v3_rsi_short_width-win_up-BTC | rsi | short | 1h | BTC | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v3_rsi_short_width param sensitivity test |
| 210 | T1 | T1-PS-v3_rsi_short_width-win_up-ETH | rsi | short | 1h | ETH | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v3_rsi_short_width param sensitivity test |
| 211 | T1 | T1-PS-v3_rsi_short_width-win_up-SOL | rsi | short | 1h | SOL | 2024-H2 | stack_canonical | window *= 1.2 | 20% | stack v3_rsi_short_width param sensitivity test |
| 212 | T1 | T1-PS-v3_rsi_short_width-win_down-BTC | rsi | short | 1h | BTC | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v3_rsi_short_width param sensitivity test |
| 213 | T1 | T1-PS-v3_rsi_short_width-win_down-ETH | rsi | short | 1h | ETH | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v3_rsi_short_width param sensitivity test |
| 214 | T1 | T1-PS-v3_rsi_short_width-win_down-SOL | rsi | short | 1h | SOL | 2024-H2 | stack_canonical | window *= 0.83 | 20% | stack v3_rsi_short_width param sensitivity test |
| 215 | T1 | T1-PS-v3_rsi_short_width-ns_up-BTC | rsi | short | 1h | BTC | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v3_rsi_short_width param sensitivity test |
| 216 | T1 | T1-PS-v3_rsi_short_width-ns_up-ETH | rsi | short | 1h | ETH | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v3_rsi_short_width param sensitivity test |
| 217 | T1 | T1-PS-v3_rsi_short_width-ns_up-SOL | rsi | short | 1h | SOL | 2024-H2 | stack_canonical | num_std += 0.25 | 20% | stack v3_rsi_short_width param sensitivity test |
| 218 | T2 | T2-BB-15-1.5-long-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 219 | T2 | T2-BB-15-1.5-long-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 220 | T2 | T2-BB-15-1.5-long-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 221 | T2 | T2-BB-15-1.5-long-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 222 | T2 | T2-BB-15-1.5-long-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 223 | T2 | T2-BB-15-1.5-long-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 224 | T2 | T2-BB-15-1.5-long-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 225 | T2 | T2-BB-15-1.5-long-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 226 | T2 | T2-BB-15-1.5-long-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 227 | T2 | T2-BB-15-1.5-short-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 228 | T2 | T2-BB-15-1.5-short-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 229 | T2 | T2-BB-15-1.5-short-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 230 | T2 | T2-BB-15-1.5-short-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 231 | T2 | T2-BB-15-1.5-short-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 232 | T2 | T2-BB-15-1.5-short-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 233 | T2 | T2-BB-15-1.5-short-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 234 | T2 | T2-BB-15-1.5-short-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 235 | T2 | T2-BB-15-1.5-short-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=1.5 | 10% | BB grid 1h canonical TF |
| 236 | T2 | T2-BB-15-1.75-long-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 237 | T2 | T2-BB-15-1.75-long-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 238 | T2 | T2-BB-15-1.75-long-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 239 | T2 | T2-BB-15-1.75-long-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 240 | T2 | T2-BB-15-1.75-long-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 241 | T2 | T2-BB-15-1.75-long-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 242 | T2 | T2-BB-15-1.75-long-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 243 | T2 | T2-BB-15-1.75-long-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 244 | T2 | T2-BB-15-1.75-long-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 245 | T2 | T2-BB-15-1.75-short-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 246 | T2 | T2-BB-15-1.75-short-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 247 | T2 | T2-BB-15-1.75-short-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 248 | T2 | T2-BB-15-1.75-short-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 249 | T2 | T2-BB-15-1.75-short-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 250 | T2 | T2-BB-15-1.75-short-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 251 | T2 | T2-BB-15-1.75-short-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 252 | T2 | T2-BB-15-1.75-short-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 253 | T2 | T2-BB-15-1.75-short-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=1.75 | 10% | BB grid 1h canonical TF |
| 254 | T2 | T2-BB-15-2.0-long-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 255 | T2 | T2-BB-15-2.0-long-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 256 | T2 | T2-BB-15-2.0-long-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 257 | T2 | T2-BB-15-2.0-long-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 258 | T2 | T2-BB-15-2.0-long-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 259 | T2 | T2-BB-15-2.0-long-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 260 | T2 | T2-BB-15-2.0-long-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 261 | T2 | T2-BB-15-2.0-long-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 262 | T2 | T2-BB-15-2.0-long-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 263 | T2 | T2-BB-15-2.0-short-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 264 | T2 | T2-BB-15-2.0-short-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 265 | T2 | T2-BB-15-2.0-short-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 266 | T2 | T2-BB-15-2.0-short-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 267 | T2 | T2-BB-15-2.0-short-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 268 | T2 | T2-BB-15-2.0-short-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 269 | T2 | T2-BB-15-2.0-short-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 270 | T2 | T2-BB-15-2.0-short-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 271 | T2 | T2-BB-15-2.0-short-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.0 | 10% | BB grid 1h canonical TF |
| 272 | T2 | T2-BB-15-2.25-long-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 273 | T2 | T2-BB-15-2.25-long-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 274 | T2 | T2-BB-15-2.25-long-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 275 | T2 | T2-BB-15-2.25-long-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 276 | T2 | T2-BB-15-2.25-long-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 277 | T2 | T2-BB-15-2.25-long-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 278 | T2 | T2-BB-15-2.25-long-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 279 | T2 | T2-BB-15-2.25-long-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 280 | T2 | T2-BB-15-2.25-long-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 281 | T2 | T2-BB-15-2.25-short-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 282 | T2 | T2-BB-15-2.25-short-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 283 | T2 | T2-BB-15-2.25-short-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 284 | T2 | T2-BB-15-2.25-short-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 285 | T2 | T2-BB-15-2.25-short-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 286 | T2 | T2-BB-15-2.25-short-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 287 | T2 | T2-BB-15-2.25-short-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 288 | T2 | T2-BB-15-2.25-short-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 289 | T2 | T2-BB-15-2.25-short-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.25 | 10% | BB grid 1h canonical TF |
| 290 | T2 | T2-BB-15-2.5-long-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 291 | T2 | T2-BB-15-2.5-long-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 292 | T2 | T2-BB-15-2.5-long-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 293 | T2 | T2-BB-15-2.5-long-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 294 | T2 | T2-BB-15-2.5-long-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 295 | T2 | T2-BB-15-2.5-long-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 296 | T2 | T2-BB-15-2.5-long-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 297 | T2 | T2-BB-15-2.5-long-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 298 | T2 | T2-BB-15-2.5-long-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 299 | T2 | T2-BB-15-2.5-short-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 300 | T2 | T2-BB-15-2.5-short-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 301 | T2 | T2-BB-15-2.5-short-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 302 | T2 | T2-BB-15-2.5-short-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 303 | T2 | T2-BB-15-2.5-short-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 304 | T2 | T2-BB-15-2.5-short-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 305 | T2 | T2-BB-15-2.5-short-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 306 | T2 | T2-BB-15-2.5-short-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 307 | T2 | T2-BB-15-2.5-short-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width_basic | window=15,num_std=2.5 | 10% | BB grid 1h canonical TF |
| 308 | T2 | T2-RSI-7-20-80-long-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 309 | T2 | T2-RSI-7-20-80-long-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 310 | T2 | T2-RSI-7-20-80-long-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 311 | T2 | T2-RSI-7-20-80-long-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 312 | T2 | T2-RSI-7-20-80-long-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 313 | T2 | T2-RSI-7-20-80-long-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 314 | T2 | T2-RSI-7-20-80-long-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 315 | T2 | T2-RSI-7-20-80-long-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 316 | T2 | T2-RSI-7-20-80-long-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 317 | T2 | T2-RSI-7-20-80-short-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 318 | T2 | T2-RSI-7-20-80-short-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 319 | T2 | T2-RSI-7-20-80-short-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 320 | T2 | T2-RSI-7-20-80-short-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 321 | T2 | T2-RSI-7-20-80-short-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 322 | T2 | T2-RSI-7-20-80-short-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 323 | T2 | T2-RSI-7-20-80-short-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 324 | T2 | T2-RSI-7-20-80-short-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 325 | T2 | T2-RSI-7-20-80-short-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width_basic | period=7,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 326 | T2 | T2-RSI-7-25-75-long-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 327 | T2 | T2-RSI-7-25-75-long-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 328 | T2 | T2-RSI-7-25-75-long-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 329 | T2 | T2-RSI-7-25-75-long-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 330 | T2 | T2-RSI-7-25-75-long-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 331 | T2 | T2-RSI-7-25-75-long-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 332 | T2 | T2-RSI-7-25-75-long-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 333 | T2 | T2-RSI-7-25-75-long-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 334 | T2 | T2-RSI-7-25-75-long-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 335 | T2 | T2-RSI-7-25-75-short-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 336 | T2 | T2-RSI-7-25-75-short-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 337 | T2 | T2-RSI-7-25-75-short-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 338 | T2 | T2-RSI-7-25-75-short-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 339 | T2 | T2-RSI-7-25-75-short-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 340 | T2 | T2-RSI-7-25-75-short-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 341 | T2 | T2-RSI-7-25-75-short-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 342 | T2 | T2-RSI-7-25-75-short-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 343 | T2 | T2-RSI-7-25-75-short-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width_basic | period=7,os=25,ob=75 | 10% | RSI grid 1h canonical TF |
| 344 | T2 | T2-RSI-7-30-70-long-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 345 | T2 | T2-RSI-7-30-70-long-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 346 | T2 | T2-RSI-7-30-70-long-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 347 | T2 | T2-RSI-7-30-70-long-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 348 | T2 | T2-RSI-7-30-70-long-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 349 | T2 | T2-RSI-7-30-70-long-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 350 | T2 | T2-RSI-7-30-70-long-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 351 | T2 | T2-RSI-7-30-70-long-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 352 | T2 | T2-RSI-7-30-70-long-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 353 | T2 | T2-RSI-7-30-70-short-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 354 | T2 | T2-RSI-7-30-70-short-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 355 | T2 | T2-RSI-7-30-70-short-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 356 | T2 | T2-RSI-7-30-70-short-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 357 | T2 | T2-RSI-7-30-70-short-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 358 | T2 | T2-RSI-7-30-70-short-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 359 | T2 | T2-RSI-7-30-70-short-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 360 | T2 | T2-RSI-7-30-70-short-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 361 | T2 | T2-RSI-7-30-70-short-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width_basic | period=7,os=30,ob=70 | 10% | RSI grid 1h canonical TF |
| 362 | T2 | T2-RSI-7-35-65-long-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 363 | T2 | T2-RSI-7-35-65-long-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 364 | T2 | T2-RSI-7-35-65-long-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 365 | T2 | T2-RSI-7-35-65-long-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 366 | T2 | T2-RSI-7-35-65-long-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 367 | T2 | T2-RSI-7-35-65-long-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 368 | T2 | T2-RSI-7-35-65-long-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 369 | T2 | T2-RSI-7-35-65-long-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 370 | T2 | T2-RSI-7-35-65-long-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 371 | T2 | T2-RSI-7-35-65-short-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 372 | T2 | T2-RSI-7-35-65-short-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 373 | T2 | T2-RSI-7-35-65-short-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 374 | T2 | T2-RSI-7-35-65-short-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 375 | T2 | T2-RSI-7-35-65-short-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 376 | T2 | T2-RSI-7-35-65-short-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 377 | T2 | T2-RSI-7-35-65-short-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 378 | T2 | T2-RSI-7-35-65-short-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 379 | T2 | T2-RSI-7-35-65-short-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width_basic | period=7,os=35,ob=65 | 10% | RSI grid 1h canonical TF |
| 380 | T2 | T2-RSI-10-20-80-long-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 381 | T2 | T2-RSI-10-20-80-long-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 382 | T2 | T2-RSI-10-20-80-long-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 383 | T2 | T2-RSI-10-20-80-long-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 384 | T2 | T2-RSI-10-20-80-long-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 385 | T2 | T2-RSI-10-20-80-long-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 386 | T2 | T2-RSI-10-20-80-long-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 387 | T2 | T2-RSI-10-20-80-long-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 388 | T2 | T2-RSI-10-20-80-long-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 389 | T2 | T2-RSI-10-20-80-short-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 390 | T2 | T2-RSI-10-20-80-short-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 391 | T2 | T2-RSI-10-20-80-short-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 392 | T2 | T2-RSI-10-20-80-short-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 393 | T2 | T2-RSI-10-20-80-short-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 394 | T2 | T2-RSI-10-20-80-short-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 395 | T2 | T2-RSI-10-20-80-short-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 396 | T2 | T2-RSI-10-20-80-short-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 397 | T2 | T2-RSI-10-20-80-short-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width_basic | period=10,os=20,ob=80 | 10% | RSI grid 1h canonical TF |
| 398 | T2 | T2-F-bollinger-long-8488-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 399 | T2 | T2-F-bollinger-long-8488-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 400 | T2 | T2-F-bollinger-long-8488-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 401 | T2 | T2-F-bollinger-long-8488-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 402 | T2 | T2-F-bollinger-long-8488-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 403 | T2 | T2-F-bollinger-long-8488-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 404 | T2 | T2-F-bollinger-long-8488-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 405 | T2 | T2-F-bollinger-long-8488-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 406 | T2 | T2-F-bollinger-long-8488-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 407 | T2 | T2-F-bollinger-short-8488-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 408 | T2 | T2-F-bollinger-short-8488-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 409 | T2 | T2-F-bollinger-short-8488-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 410 | T2 | T2-F-bollinger-short-8488-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 411 | T2 | T2-F-bollinger-short-8488-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 412 | T2 | T2-F-bollinger-short-8488-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 413 | T2 | T2-F-bollinger-short-8488-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 414 | T2 | T2-F-bollinger-short-8488-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 415 | T2 | T2-F-bollinger-short-8488-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 416 | T2 | T2-F-rsi-long-8488-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 417 | T2 | T2-F-rsi-long-8488-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 418 | T2 | T2-F-rsi-long-8488-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 419 | T2 | T2-F-rsi-long-8488-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 420 | T2 | T2-F-rsi-long-8488-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 421 | T2 | T2-F-rsi-long-8488-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 422 | T2 | T2-F-rsi-long-8488-SOL-2024-H2 | rsi | long | 1h | SOL | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 423 | T2 | T2-F-rsi-long-8488-SOL-2025-H1 | rsi | long | 1h | SOL | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 424 | T2 | T2-F-rsi-long-8488-SOL-2025-H2 | rsi | long | 1h | SOL | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 425 | T2 | T2-F-rsi-short-8488-BTC-2024-H2 | rsi | short | 1h | BTC | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 426 | T2 | T2-F-rsi-short-8488-BTC-2025-H1 | rsi | short | 1h | BTC | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 427 | T2 | T2-F-rsi-short-8488-BTC-2025-H2 | rsi | short | 1h | BTC | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 428 | T2 | T2-F-rsi-short-8488-ETH-2024-H2 | rsi | short | 1h | ETH | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 429 | T2 | T2-F-rsi-short-8488-ETH-2025-H1 | rsi | short | 1h | ETH | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 430 | T2 | T2-F-rsi-short-8488-ETH-2025-H2 | rsi | short | 1h | ETH | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 431 | T2 | T2-F-rsi-short-8488-SOL-2024-H2 | rsi | short | 1h | SOL | 2024-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 432 | T2 | T2-F-rsi-short-8488-SOL-2025-H1 | rsi | short | 1h | SOL | 2025-H1 | width:min=100 | canonical | 12% | filter combination sweep |
| 433 | T2 | T2-F-rsi-short-8488-SOL-2025-H2 | rsi | short | 1h | SOL | 2025-H2 | width:min=100 | canonical | 12% | filter combination sweep |
| 434 | T2 | T2-F-bollinger-long-3887-BTC-2024-H2 | bollinger | long | 1h | BTC | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 435 | T2 | T2-F-bollinger-long-3887-BTC-2025-H1 | bollinger | long | 1h | BTC | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 436 | T2 | T2-F-bollinger-long-3887-BTC-2025-H2 | bollinger | long | 1h | BTC | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 437 | T2 | T2-F-bollinger-long-3887-ETH-2024-H2 | bollinger | long | 1h | ETH | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 438 | T2 | T2-F-bollinger-long-3887-ETH-2025-H1 | bollinger | long | 1h | ETH | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 439 | T2 | T2-F-bollinger-long-3887-ETH-2025-H2 | bollinger | long | 1h | ETH | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 440 | T2 | T2-F-bollinger-long-3887-SOL-2024-H2 | bollinger | long | 1h | SOL | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 441 | T2 | T2-F-bollinger-long-3887-SOL-2025-H1 | bollinger | long | 1h | SOL | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 442 | T2 | T2-F-bollinger-long-3887-SOL-2025-H2 | bollinger | long | 1h | SOL | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 443 | T2 | T2-F-bollinger-short-3887-BTC-2024-H2 | bollinger | short | 1h | BTC | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 444 | T2 | T2-F-bollinger-short-3887-BTC-2025-H1 | bollinger | short | 1h | BTC | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 445 | T2 | T2-F-bollinger-short-3887-BTC-2025-H2 | bollinger | short | 1h | BTC | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 446 | T2 | T2-F-bollinger-short-3887-ETH-2024-H2 | bollinger | short | 1h | ETH | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 447 | T2 | T2-F-bollinger-short-3887-ETH-2025-H1 | bollinger | short | 1h | ETH | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 448 | T2 | T2-F-bollinger-short-3887-ETH-2025-H2 | bollinger | short | 1h | ETH | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 449 | T2 | T2-F-bollinger-short-3887-SOL-2024-H2 | bollinger | short | 1h | SOL | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 450 | T2 | T2-F-bollinger-short-3887-SOL-2025-H1 | bollinger | short | 1h | SOL | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 451 | T2 | T2-F-bollinger-short-3887-SOL-2025-H2 | bollinger | short | 1h | SOL | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 452 | T2 | T2-F-rsi-long-3887-BTC-2024-H2 | rsi | long | 1h | BTC | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 453 | T2 | T2-F-rsi-long-3887-BTC-2025-H1 | rsi | long | 1h | BTC | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 454 | T2 | T2-F-rsi-long-3887-BTC-2025-H2 | rsi | long | 1h | BTC | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 455 | T2 | T2-F-rsi-long-3887-ETH-2024-H2 | rsi | long | 1h | ETH | 2024-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 456 | T2 | T2-F-rsi-long-3887-ETH-2025-H1 | rsi | long | 1h | ETH | 2025-H1 | width:min=150 | canonical | 12% | filter combination sweep |
| 457 | T2 | T2-F-rsi-long-3887-ETH-2025-H2 | rsi | long | 1h | ETH | 2025-H2 | width:min=150 | canonical | 12% | filter combination sweep |
| 458 | T2 | T2-COMP-15-1.5-25-75-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 459 | T2 | T2-COMP-15-1.5-25-75-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 460 | T2 | T2-COMP-15-1.5-25-75-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 461 | T2 | T2-COMP-15-1.5-25-75-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 462 | T2 | T2-COMP-15-1.5-25-75-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 463 | T2 | T2-COMP-15-1.5-25-75-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 464 | T2 | T2-COMP-15-1.5-25-75-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 465 | T2 | T2-COMP-15-1.5-25-75-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 466 | T2 | T2-COMP-15-1.5-25-75-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 467 | T2 | T2-COMP-15-1.5-30-70-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 468 | T2 | T2-COMP-15-1.5-30-70-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 469 | T2 | T2-COMP-15-1.5-30-70-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 470 | T2 | T2-COMP-15-1.5-30-70-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 471 | T2 | T2-COMP-15-1.5-30-70-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 472 | T2 | T2-COMP-15-1.5-30-70-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 473 | T2 | T2-COMP-15-1.5-30-70-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 474 | T2 | T2-COMP-15-1.5-30-70-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 475 | T2 | T2-COMP-15-1.5-30-70-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 476 | T2 | T2-COMP-15-1.5-35-65-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 477 | T2 | T2-COMP-15-1.5-35-65-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 478 | T2 | T2-COMP-15-1.5-35-65-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 479 | T2 | T2-COMP-15-1.5-35-65-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 480 | T2 | T2-COMP-15-1.5-35-65-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 481 | T2 | T2-COMP-15-1.5-35-65-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 482 | T2 | T2-COMP-15-1.5-35-65-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 483 | T2 | T2-COMP-15-1.5-35-65-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 484 | T2 | T2-COMP-15-1.5-35-65-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=1.5,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 485 | T2 | T2-COMP-15-2.0-25-75-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 486 | T2 | T2-COMP-15-2.0-25-75-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 487 | T2 | T2-COMP-15-2.0-25-75-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 488 | T2 | T2-COMP-15-2.0-25-75-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 489 | T2 | T2-COMP-15-2.0-25-75-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 490 | T2 | T2-COMP-15-2.0-25-75-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 491 | T2 | T2-COMP-15-2.0-25-75-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 492 | T2 | T2-COMP-15-2.0-25-75-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 493 | T2 | T2-COMP-15-2.0-25-75-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 494 | T2 | T2-COMP-15-2.0-30-70-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 495 | T2 | T2-COMP-15-2.0-30-70-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 496 | T2 | T2-COMP-15-2.0-30-70-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 497 | T2 | T2-COMP-15-2.0-30-70-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 498 | T2 | T2-COMP-15-2.0-30-70-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 499 | T2 | T2-COMP-15-2.0-30-70-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 500 | T2 | T2-COMP-15-2.0-30-70-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 501 | T2 | T2-COMP-15-2.0-30-70-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 502 | T2 | T2-COMP-15-2.0-30-70-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=30,rsi_ob=70 | 10% | composite MR 1h param grid |
| 503 | T2 | T2-COMP-15-2.0-35-65-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 504 | T2 | T2-COMP-15-2.0-35-65-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 505 | T2 | T2-COMP-15-2.0-35-65-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 506 | T2 | T2-COMP-15-2.0-35-65-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 507 | T2 | T2-COMP-15-2.0-35-65-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 508 | T2 | T2-COMP-15-2.0-35-65-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 509 | T2 | T2-COMP-15-2.0-35-65-SOL-2024-H2 | composite_bb_rsi | short | 1h | SOL | 2024-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 510 | T2 | T2-COMP-15-2.0-35-65-SOL-2025-H1 | composite_bb_rsi | short | 1h | SOL | 2025-H1 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 511 | T2 | T2-COMP-15-2.0-35-65-SOL-2025-H2 | composite_bb_rsi | short | 1h | SOL | 2025-H2 | none | bb_w=15,bb_ns=2.0,rsi_os=35,rsi_ob=65 | 10% | composite MR 1h param grid |
| 512 | T2 | T2-COMP-15-2.5-25-75-BTC-2024-H2 | composite_bb_rsi | short | 1h | BTC | 2024-H2 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 513 | T2 | T2-COMP-15-2.5-25-75-BTC-2025-H1 | composite_bb_rsi | short | 1h | BTC | 2025-H1 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 514 | T2 | T2-COMP-15-2.5-25-75-BTC-2025-H2 | composite_bb_rsi | short | 1h | BTC | 2025-H2 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 515 | T2 | T2-COMP-15-2.5-25-75-ETH-2024-H2 | composite_bb_rsi | short | 1h | ETH | 2024-H2 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 516 | T2 | T2-COMP-15-2.5-25-75-ETH-2025-H1 | composite_bb_rsi | short | 1h | ETH | 2025-H1 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 517 | T2 | T2-COMP-15-2.5-25-75-ETH-2025-H2 | composite_bb_rsi | short | 1h | ETH | 2025-H2 | none | bb_w=15,bb_ns=2.5,rsi_os=25,rsi_ob=75 | 10% | composite MR 1h param grid |
| 518 | T3 | T3-TF-ma_crossover-5m-BTC-2024-H2 | ma_crossover | long | 5m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 519 | T3 | T3-TF-ma_crossover-5m-BTC-2025-H1 | ma_crossover | long | 5m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 520 | T3 | T3-TF-ma_crossover-5m-BTC-2025-H2 | ma_crossover | long | 5m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 521 | T3 | T3-TF-ma_crossover-5m-ETH-2024-H2 | ma_crossover | long | 5m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 522 | T3 | T3-TF-ma_crossover-5m-ETH-2025-H1 | ma_crossover | long | 5m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 523 | T3 | T3-TF-ma_crossover-5m-ETH-2025-H2 | ma_crossover | long | 5m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 524 | T3 | T3-TF-ma_crossover-5m-SOL-2024-H2 | ma_crossover | long | 5m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 525 | T3 | T3-TF-ma_crossover-5m-SOL-2025-H1 | ma_crossover | long | 5m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 526 | T3 | T3-TF-ma_crossover-5m-SOL-2025-H2 | ma_crossover | long | 5m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 527 | T3 | T3-TF-ma_crossover-15m-BTC-2024-H2 | ma_crossover | long | 15m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 528 | T3 | T3-TF-ma_crossover-15m-BTC-2025-H1 | ma_crossover | long | 15m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 529 | T3 | T3-TF-ma_crossover-15m-BTC-2025-H2 | ma_crossover | long | 15m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 530 | T3 | T3-TF-ma_crossover-15m-ETH-2024-H2 | ma_crossover | long | 15m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 531 | T3 | T3-TF-ma_crossover-15m-ETH-2025-H1 | ma_crossover | long | 15m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 532 | T3 | T3-TF-ma_crossover-15m-ETH-2025-H2 | ma_crossover | long | 15m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 533 | T3 | T3-TF-ma_crossover-15m-SOL-2024-H2 | ma_crossover | long | 15m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 534 | T3 | T3-TF-ma_crossover-15m-SOL-2025-H1 | ma_crossover | long | 15m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 535 | T3 | T3-TF-ma_crossover-15m-SOL-2025-H2 | ma_crossover | long | 15m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 536 | T3 | T3-TF-ma_crossover-30m-BTC-2024-H2 | ma_crossover | long | 30m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 537 | T3 | T3-TF-ma_crossover-30m-BTC-2025-H1 | ma_crossover | long | 30m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 538 | T3 | T3-TF-ma_crossover-30m-BTC-2025-H2 | ma_crossover | long | 30m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 539 | T3 | T3-TF-ma_crossover-30m-ETH-2024-H2 | ma_crossover | long | 30m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 540 | T3 | T3-TF-ma_crossover-30m-ETH-2025-H1 | ma_crossover | long | 30m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 541 | T3 | T3-TF-ma_crossover-30m-ETH-2025-H2 | ma_crossover | long | 30m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 542 | T3 | T3-TF-ma_crossover-30m-SOL-2024-H2 | ma_crossover | long | 30m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 543 | T3 | T3-TF-ma_crossover-30m-SOL-2025-H1 | ma_crossover | long | 30m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 544 | T3 | T3-TF-ma_crossover-30m-SOL-2025-H2 | ma_crossover | long | 30m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 545 | T3 | T3-TF-ma_crossover-4h-BTC-2024-H2 | ma_crossover | long | 4h | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 546 | T3 | T3-TF-ma_crossover-4h-BTC-2025-H1 | ma_crossover | long | 4h | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 547 | T3 | T3-TF-ma_crossover-4h-BTC-2025-H2 | ma_crossover | long | 4h | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 548 | T3 | T3-TF-ma_crossover-4h-ETH-2024-H2 | ma_crossover | long | 4h | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 549 | T3 | T3-TF-ma_crossover-4h-ETH-2025-H1 | ma_crossover | long | 4h | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 550 | T3 | T3-TF-ma_crossover-4h-ETH-2025-H2 | ma_crossover | long | 4h | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 551 | T3 | T3-TF-ma_crossover-4h-SOL-2024-H2 | ma_crossover | long | 4h | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 552 | T3 | T3-TF-ma_crossover-4h-SOL-2025-H1 | ma_crossover | long | 4h | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 553 | T3 | T3-TF-ma_crossover-4h-SOL-2025-H2 | ma_crossover | long | 4h | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 554 | T3 | T3-TF-supertrend-5m-BTC-2024-H2 | supertrend | bi | 5m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 555 | T3 | T3-TF-supertrend-5m-BTC-2025-H1 | supertrend | bi | 5m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 556 | T3 | T3-TF-supertrend-5m-BTC-2025-H2 | supertrend | bi | 5m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 557 | T3 | T3-TF-supertrend-5m-ETH-2024-H2 | supertrend | bi | 5m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 558 | T3 | T3-TF-supertrend-5m-ETH-2025-H1 | supertrend | bi | 5m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 559 | T3 | T3-TF-supertrend-5m-ETH-2025-H2 | supertrend | bi | 5m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 560 | T3 | T3-TF-supertrend-5m-SOL-2024-H2 | supertrend | bi | 5m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 561 | T3 | T3-TF-supertrend-5m-SOL-2025-H1 | supertrend | bi | 5m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 562 | T3 | T3-TF-supertrend-5m-SOL-2025-H2 | supertrend | bi | 5m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 563 | T3 | T3-TF-supertrend-15m-BTC-2024-H2 | supertrend | bi | 15m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 564 | T3 | T3-TF-supertrend-15m-BTC-2025-H1 | supertrend | bi | 15m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 565 | T3 | T3-TF-supertrend-15m-BTC-2025-H2 | supertrend | bi | 15m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 566 | T3 | T3-TF-supertrend-15m-ETH-2024-H2 | supertrend | bi | 15m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 567 | T3 | T3-TF-supertrend-15m-ETH-2025-H1 | supertrend | bi | 15m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 568 | T3 | T3-TF-supertrend-15m-ETH-2025-H2 | supertrend | bi | 15m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 569 | T3 | T3-TF-supertrend-15m-SOL-2024-H2 | supertrend | bi | 15m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 570 | T3 | T3-TF-supertrend-15m-SOL-2025-H1 | supertrend | bi | 15m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 571 | T3 | T3-TF-supertrend-15m-SOL-2025-H2 | supertrend | bi | 15m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 572 | T3 | T3-TF-supertrend-30m-BTC-2024-H2 | supertrend | bi | 30m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 573 | T3 | T3-TF-supertrend-30m-BTC-2025-H1 | supertrend | bi | 30m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 574 | T3 | T3-TF-supertrend-30m-BTC-2025-H2 | supertrend | bi | 30m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 575 | T3 | T3-TF-supertrend-30m-ETH-2024-H2 | supertrend | bi | 30m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 576 | T3 | T3-TF-supertrend-30m-ETH-2025-H1 | supertrend | bi | 30m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 577 | T3 | T3-TF-supertrend-30m-ETH-2025-H2 | supertrend | bi | 30m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 578 | T3 | T3-TF-supertrend-30m-SOL-2024-H2 | supertrend | bi | 30m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 579 | T3 | T3-TF-supertrend-30m-SOL-2025-H1 | supertrend | bi | 30m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 580 | T3 | T3-TF-supertrend-30m-SOL-2025-H2 | supertrend | bi | 30m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 581 | T3 | T3-TF-supertrend-4h-BTC-2024-H2 | supertrend | bi | 4h | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 582 | T3 | T3-TF-supertrend-4h-BTC-2025-H1 | supertrend | bi | 4h | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 583 | T3 | T3-TF-supertrend-4h-BTC-2025-H2 | supertrend | bi | 4h | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 584 | T3 | T3-TF-supertrend-4h-ETH-2024-H2 | supertrend | bi | 4h | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 585 | T3 | T3-TF-supertrend-4h-ETH-2025-H1 | supertrend | bi | 4h | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 586 | T3 | T3-TF-supertrend-4h-ETH-2025-H2 | supertrend | bi | 4h | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 587 | T3 | T3-TF-supertrend-4h-SOL-2024-H2 | supertrend | bi | 4h | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 588 | T3 | T3-TF-supertrend-4h-SOL-2025-H1 | supertrend | bi | 4h | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 4h |
| 589 | T3 | T3-TF-supertrend-4h-SOL-2025-H2 | supertrend | bi | 4h | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 590 | T3 | T3-TF-donchian-5m-BTC-2024-H2 | donchian | long | 5m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 591 | T3 | T3-TF-donchian-5m-BTC-2025-H1 | donchian | long | 5m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 592 | T3 | T3-TF-donchian-5m-BTC-2025-H2 | donchian | long | 5m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 593 | T3 | T3-TF-donchian-5m-ETH-2024-H2 | donchian | long | 5m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 594 | T3 | T3-TF-donchian-5m-ETH-2025-H1 | donchian | long | 5m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 595 | T3 | T3-TF-donchian-5m-ETH-2025-H2 | donchian | long | 5m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 596 | T3 | T3-TF-donchian-5m-SOL-2024-H2 | donchian | long | 5m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 597 | T3 | T3-TF-donchian-5m-SOL-2025-H1 | donchian | long | 5m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 5m |
| 598 | T3 | T3-TF-donchian-5m-SOL-2025-H2 | donchian | long | 5m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 5m |
| 599 | T3 | T3-TF-donchian-15m-BTC-2024-H2 | donchian | long | 15m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 600 | T3 | T3-TF-donchian-15m-BTC-2025-H1 | donchian | long | 15m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 601 | T3 | T3-TF-donchian-15m-BTC-2025-H2 | donchian | long | 15m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 602 | T3 | T3-TF-donchian-15m-ETH-2024-H2 | donchian | long | 15m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 603 | T3 | T3-TF-donchian-15m-ETH-2025-H1 | donchian | long | 15m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 604 | T3 | T3-TF-donchian-15m-ETH-2025-H2 | donchian | long | 15m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 605 | T3 | T3-TF-donchian-15m-SOL-2024-H2 | donchian | long | 15m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 606 | T3 | T3-TF-donchian-15m-SOL-2025-H1 | donchian | long | 15m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 15m |
| 607 | T3 | T3-TF-donchian-15m-SOL-2025-H2 | donchian | long | 15m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 15m |
| 608 | T3 | T3-TF-donchian-30m-BTC-2024-H2 | donchian | long | 30m | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 609 | T3 | T3-TF-donchian-30m-BTC-2025-H1 | donchian | long | 30m | BTC | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 610 | T3 | T3-TF-donchian-30m-BTC-2025-H2 | donchian | long | 30m | BTC | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 611 | T3 | T3-TF-donchian-30m-ETH-2024-H2 | donchian | long | 30m | ETH | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 612 | T3 | T3-TF-donchian-30m-ETH-2025-H1 | donchian | long | 30m | ETH | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 613 | T3 | T3-TF-donchian-30m-ETH-2025-H2 | donchian | long | 30m | ETH | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 614 | T3 | T3-TF-donchian-30m-SOL-2024-H2 | donchian | long | 30m | SOL | 2024-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 615 | T3 | T3-TF-donchian-30m-SOL-2025-H1 | donchian | long | 30m | SOL | 2025-H1 | none | canonical | 5% | gap coverage non-MR 30m |
| 616 | T3 | T3-TF-donchian-30m-SOL-2025-H2 | donchian | long | 30m | SOL | 2025-H2 | none | canonical | 5% | gap coverage non-MR 30m |
| 617 | T3 | T3-TF-donchian-4h-BTC-2024-H2 | donchian | long | 4h | BTC | 2024-H2 | none | canonical | 5% | gap coverage non-MR 4h |
| 618 | T3 | T3-SHORT-ma_crossover-10m-BTC-2024-H2 | ma_crossover | short | 10m | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 619 | T3 | T3-SHORT-ma_crossover-10m-BTC-2025-H1 | ma_crossover | short | 10m | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 620 | T3 | T3-SHORT-ma_crossover-10m-BTC-2025-H2 | ma_crossover | short | 10m | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 621 | T3 | T3-SHORT-ma_crossover-10m-ETH-2024-H2 | ma_crossover | short | 10m | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 622 | T3 | T3-SHORT-ma_crossover-10m-ETH-2025-H1 | ma_crossover | short | 10m | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 623 | T3 | T3-SHORT-ma_crossover-10m-ETH-2025-H2 | ma_crossover | short | 10m | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 624 | T3 | T3-SHORT-ma_crossover-10m-SOL-2024-H2 | ma_crossover | short | 10m | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 625 | T3 | T3-SHORT-ma_crossover-10m-SOL-2025-H1 | ma_crossover | short | 10m | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 626 | T3 | T3-SHORT-ma_crossover-10m-SOL-2025-H2 | ma_crossover | short | 10m | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 627 | T3 | T3-SHORT-ma_crossover-30m-BTC-2024-H2 | ma_crossover | short | 30m | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 628 | T3 | T3-SHORT-ma_crossover-30m-BTC-2025-H1 | ma_crossover | short | 30m | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 629 | T3 | T3-SHORT-ma_crossover-30m-BTC-2025-H2 | ma_crossover | short | 30m | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 630 | T3 | T3-SHORT-ma_crossover-30m-ETH-2024-H2 | ma_crossover | short | 30m | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 631 | T3 | T3-SHORT-ma_crossover-30m-ETH-2025-H1 | ma_crossover | short | 30m | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 632 | T3 | T3-SHORT-ma_crossover-30m-ETH-2025-H2 | ma_crossover | short | 30m | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 633 | T3 | T3-SHORT-ma_crossover-30m-SOL-2024-H2 | ma_crossover | short | 30m | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 634 | T3 | T3-SHORT-ma_crossover-30m-SOL-2025-H1 | ma_crossover | short | 30m | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 635 | T3 | T3-SHORT-ma_crossover-30m-SOL-2025-H2 | ma_crossover | short | 30m | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 636 | T3 | T3-SHORT-ma_crossover-1h-BTC-2024-H2 | ma_crossover | short | 1h | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 637 | T3 | T3-SHORT-ma_crossover-1h-BTC-2025-H1 | ma_crossover | short | 1h | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 638 | T3 | T3-SHORT-ma_crossover-1h-BTC-2025-H2 | ma_crossover | short | 1h | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 639 | T3 | T3-SHORT-ma_crossover-1h-ETH-2024-H2 | ma_crossover | short | 1h | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 640 | T3 | T3-SHORT-ma_crossover-1h-ETH-2025-H1 | ma_crossover | short | 1h | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 641 | T3 | T3-SHORT-ma_crossover-1h-ETH-2025-H2 | ma_crossover | short | 1h | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 642 | T3 | T3-SHORT-ma_crossover-1h-SOL-2024-H2 | ma_crossover | short | 1h | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 643 | T3 | T3-SHORT-ma_crossover-1h-SOL-2025-H1 | ma_crossover | short | 1h | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 644 | T3 | T3-SHORT-ma_crossover-1h-SOL-2025-H2 | ma_crossover | short | 1h | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 645 | T3 | T3-SHORT-ma_crossover-4h-BTC-2024-H2 | ma_crossover | short | 4h | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 646 | T3 | T3-SHORT-ma_crossover-4h-BTC-2025-H1 | ma_crossover | short | 4h | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 647 | T3 | T3-SHORT-ma_crossover-4h-BTC-2025-H2 | ma_crossover | short | 4h | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 648 | T3 | T3-SHORT-ma_crossover-4h-ETH-2024-H2 | ma_crossover | short | 4h | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 649 | T3 | T3-SHORT-ma_crossover-4h-ETH-2025-H1 | ma_crossover | short | 4h | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 650 | T3 | T3-SHORT-ma_crossover-4h-ETH-2025-H2 | ma_crossover | short | 4h | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 651 | T3 | T3-SHORT-ma_crossover-4h-SOL-2024-H2 | ma_crossover | short | 4h | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 652 | T3 | T3-SHORT-ma_crossover-4h-SOL-2025-H1 | ma_crossover | short | 4h | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 653 | T3 | T3-SHORT-ma_crossover-4h-SOL-2025-H2 | ma_crossover | short | 4h | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 654 | T3 | T3-SHORT-donchian-10m-BTC-2024-H2 | donchian | short | 10m | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 655 | T3 | T3-SHORT-donchian-10m-BTC-2025-H1 | donchian | short | 10m | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 656 | T3 | T3-SHORT-donchian-10m-BTC-2025-H2 | donchian | short | 10m | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 657 | T3 | T3-SHORT-donchian-10m-ETH-2024-H2 | donchian | short | 10m | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 658 | T3 | T3-SHORT-donchian-10m-ETH-2025-H1 | donchian | short | 10m | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 659 | T3 | T3-SHORT-donchian-10m-ETH-2025-H2 | donchian | short | 10m | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 660 | T3 | T3-SHORT-donchian-10m-SOL-2024-H2 | donchian | short | 10m | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 661 | T3 | T3-SHORT-donchian-10m-SOL-2025-H1 | donchian | short | 10m | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 662 | T3 | T3-SHORT-donchian-10m-SOL-2025-H2 | donchian | short | 10m | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 663 | T3 | T3-SHORT-donchian-30m-BTC-2024-H2 | donchian | short | 30m | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 664 | T3 | T3-SHORT-donchian-30m-BTC-2025-H1 | donchian | short | 30m | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 665 | T3 | T3-SHORT-donchian-30m-BTC-2025-H2 | donchian | short | 30m | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 666 | T3 | T3-SHORT-donchian-30m-ETH-2024-H2 | donchian | short | 30m | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 667 | T3 | T3-SHORT-donchian-30m-ETH-2025-H1 | donchian | short | 30m | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 668 | T3 | T3-SHORT-donchian-30m-ETH-2025-H2 | donchian | short | 30m | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 669 | T3 | T3-SHORT-donchian-30m-SOL-2024-H2 | donchian | short | 30m | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 670 | T3 | T3-SHORT-donchian-30m-SOL-2025-H1 | donchian | short | 30m | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 671 | T3 | T3-SHORT-donchian-30m-SOL-2025-H2 | donchian | short | 30m | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 672 | T3 | T3-SHORT-donchian-1h-BTC-2024-H2 | donchian | short | 1h | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 673 | T3 | T3-SHORT-donchian-1h-BTC-2025-H1 | donchian | short | 1h | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 674 | T3 | T3-SHORT-donchian-1h-BTC-2025-H2 | donchian | short | 1h | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 675 | T3 | T3-SHORT-donchian-1h-ETH-2024-H2 | donchian | short | 1h | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 676 | T3 | T3-SHORT-donchian-1h-ETH-2025-H1 | donchian | short | 1h | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 677 | T3 | T3-SHORT-donchian-1h-ETH-2025-H2 | donchian | short | 1h | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 678 | T3 | T3-SHORT-donchian-1h-SOL-2024-H2 | donchian | short | 1h | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 679 | T3 | T3-SHORT-donchian-1h-SOL-2025-H1 | donchian | short | 1h | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 680 | T3 | T3-SHORT-donchian-1h-SOL-2025-H2 | donchian | short | 1h | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 681 | T3 | T3-SHORT-donchian-4h-BTC-2024-H2 | donchian | short | 4h | BTC | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 682 | T3 | T3-SHORT-donchian-4h-BTC-2025-H1 | donchian | short | 4h | BTC | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 683 | T3 | T3-SHORT-donchian-4h-BTC-2025-H2 | donchian | short | 4h | BTC | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 684 | T3 | T3-SHORT-donchian-4h-ETH-2024-H2 | donchian | short | 4h | ETH | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 685 | T3 | T3-SHORT-donchian-4h-ETH-2025-H1 | donchian | short | 4h | ETH | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 686 | T3 | T3-SHORT-donchian-4h-ETH-2025-H2 | donchian | short | 4h | ETH | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 687 | T3 | T3-SHORT-donchian-4h-SOL-2024-H2 | donchian | short | 4h | SOL | 2024-H2 | none | canonical | 5% | short variants de engines long-default |
| 688 | T3 | T3-SHORT-donchian-4h-SOL-2025-H1 | donchian | short | 4h | SOL | 2025-H1 | none | canonical | 5% | short variants de engines long-default |
| 689 | T3 | T3-SHORT-donchian-4h-SOL-2025-H2 | donchian | short | 4h | SOL | 2025-H2 | none | canonical | 5% | short variants de engines long-default |
| 690 | T3 | T3-KELT-20-14-2.5-BTC-2024-H2 | keltner | bi | 1h | BTC | 2024-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 691 | T3 | T3-KELT-20-14-2.5-BTC-2025-H1 | keltner | bi | 1h | BTC | 2025-H1 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 692 | T3 | T3-KELT-20-14-2.5-BTC-2025-H2 | keltner | bi | 1h | BTC | 2025-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 693 | T3 | T3-KELT-20-14-2.5-ETH-2024-H2 | keltner | bi | 1h | ETH | 2024-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 694 | T3 | T3-KELT-20-14-2.5-ETH-2025-H1 | keltner | bi | 1h | ETH | 2025-H1 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 695 | T3 | T3-KELT-20-14-2.5-ETH-2025-H2 | keltner | bi | 1h | ETH | 2025-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 696 | T3 | T3-KELT-20-14-2.5-SOL-2024-H2 | keltner | bi | 1h | SOL | 2024-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 697 | T3 | T3-KELT-20-14-2.5-SOL-2025-H1 | keltner | bi | 1h | SOL | 2025-H1 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 698 | T3 | T3-KELT-20-14-2.5-SOL-2025-H2 | keltner | bi | 1h | SOL | 2025-H2 | none | window=20,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 699 | T3 | T3-KELT-20-14-3.0-BTC-2024-H2 | keltner | bi | 1h | BTC | 2024-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 700 | T3 | T3-KELT-20-14-3.0-BTC-2025-H1 | keltner | bi | 1h | BTC | 2025-H1 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 701 | T3 | T3-KELT-20-14-3.0-BTC-2025-H2 | keltner | bi | 1h | BTC | 2025-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 702 | T3 | T3-KELT-20-14-3.0-ETH-2024-H2 | keltner | bi | 1h | ETH | 2024-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 703 | T3 | T3-KELT-20-14-3.0-ETH-2025-H1 | keltner | bi | 1h | ETH | 2025-H1 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 704 | T3 | T3-KELT-20-14-3.0-ETH-2025-H2 | keltner | bi | 1h | ETH | 2025-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 705 | T3 | T3-KELT-20-14-3.0-SOL-2024-H2 | keltner | bi | 1h | SOL | 2024-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 706 | T3 | T3-KELT-20-14-3.0-SOL-2025-H1 | keltner | bi | 1h | SOL | 2025-H1 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 707 | T3 | T3-KELT-20-14-3.0-SOL-2025-H2 | keltner | bi | 1h | SOL | 2025-H2 | none | window=20,atr_p=14,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 708 | T3 | T3-KELT-30-14-2.5-BTC-2024-H2 | keltner | bi | 1h | BTC | 2024-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 709 | T3 | T3-KELT-30-14-2.5-BTC-2025-H1 | keltner | bi | 1h | BTC | 2025-H1 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 710 | T3 | T3-KELT-30-14-2.5-BTC-2025-H2 | keltner | bi | 1h | BTC | 2025-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 711 | T3 | T3-KELT-30-14-2.5-ETH-2024-H2 | keltner | bi | 1h | ETH | 2024-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 712 | T3 | T3-KELT-30-14-2.5-ETH-2025-H1 | keltner | bi | 1h | ETH | 2025-H1 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 713 | T3 | T3-KELT-30-14-2.5-ETH-2025-H2 | keltner | bi | 1h | ETH | 2025-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 714 | T3 | T3-KELT-30-14-2.5-SOL-2024-H2 | keltner | bi | 1h | SOL | 2024-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 715 | T3 | T3-KELT-30-14-2.5-SOL-2025-H1 | keltner | bi | 1h | SOL | 2025-H1 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 716 | T3 | T3-KELT-30-14-2.5-SOL-2025-H2 | keltner | bi | 1h | SOL | 2025-H2 | none | window=30,atr_p=14,mult=2.5 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 717 | T3 | T3-KELT-30-21-3.0-BTC-2024-H2 | keltner | bi | 1h | BTC | 2024-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 718 | T3 | T3-KELT-30-21-3.0-BTC-2025-H1 | keltner | bi | 1h | BTC | 2025-H1 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 719 | T3 | T3-KELT-30-21-3.0-BTC-2025-H2 | keltner | bi | 1h | BTC | 2025-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 720 | T3 | T3-KELT-30-21-3.0-ETH-2024-H2 | keltner | bi | 1h | ETH | 2024-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 721 | T3 | T3-KELT-30-21-3.0-ETH-2025-H1 | keltner | bi | 1h | ETH | 2025-H1 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 722 | T3 | T3-KELT-30-21-3.0-ETH-2025-H2 | keltner | bi | 1h | ETH | 2025-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 723 | T3 | T3-KELT-30-21-3.0-SOL-2024-H2 | keltner | bi | 1h | SOL | 2024-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 724 | T3 | T3-KELT-30-21-3.0-SOL-2025-H1 | keltner | bi | 1h | SOL | 2025-H1 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 725 | T3 | T3-KELT-30-21-3.0-SOL-2025-H2 | keltner | bi | 1h | SOL | 2025-H2 | none | window=30,atr_p=21,mult=3.0 | 8% | Keltner param reabertura 1h thresholds restritivos |
| 726 | T3 | T3-ZS-20-2.5-BTC-2024-H2 | zscore | bi | 1h | BTC | 2024-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 727 | T3 | T3-ZS-20-2.5-BTC-2025-H1 | zscore | bi | 1h | BTC | 2025-H1 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 728 | T3 | T3-ZS-20-2.5-BTC-2025-H2 | zscore | bi | 1h | BTC | 2025-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 729 | T3 | T3-ZS-20-2.5-ETH-2024-H2 | zscore | bi | 1h | ETH | 2024-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 730 | T3 | T3-ZS-20-2.5-ETH-2025-H1 | zscore | bi | 1h | ETH | 2025-H1 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 731 | T3 | T3-ZS-20-2.5-ETH-2025-H2 | zscore | bi | 1h | ETH | 2025-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 732 | T3 | T3-ZS-20-2.5-SOL-2024-H2 | zscore | bi | 1h | SOL | 2024-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 733 | T3 | T3-ZS-20-2.5-SOL-2025-H1 | zscore | bi | 1h | SOL | 2025-H1 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 734 | T3 | T3-ZS-20-2.5-SOL-2025-H2 | zscore | bi | 1h | SOL | 2025-H2 | none | window=20,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 735 | T3 | T3-ZS-20-3.0-BTC-2024-H2 | zscore | bi | 1h | BTC | 2024-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 736 | T3 | T3-ZS-20-3.0-BTC-2025-H1 | zscore | bi | 1h | BTC | 2025-H1 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 737 | T3 | T3-ZS-20-3.0-BTC-2025-H2 | zscore | bi | 1h | BTC | 2025-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 738 | T3 | T3-ZS-20-3.0-ETH-2024-H2 | zscore | bi | 1h | ETH | 2024-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 739 | T3 | T3-ZS-20-3.0-ETH-2025-H1 | zscore | bi | 1h | ETH | 2025-H1 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 740 | T3 | T3-ZS-20-3.0-ETH-2025-H2 | zscore | bi | 1h | ETH | 2025-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 741 | T3 | T3-ZS-20-3.0-SOL-2024-H2 | zscore | bi | 1h | SOL | 2024-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 742 | T3 | T3-ZS-20-3.0-SOL-2025-H1 | zscore | bi | 1h | SOL | 2025-H1 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 743 | T3 | T3-ZS-20-3.0-SOL-2025-H2 | zscore | bi | 1h | SOL | 2025-H2 | none | window=20,threshold=3.0 | 8% | zscore param reabertura 1h thresholds restritivos |
| 744 | T3 | T3-ZS-30-2.5-BTC-2024-H2 | zscore | bi | 1h | BTC | 2024-H2 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 745 | T3 | T3-ZS-30-2.5-BTC-2025-H1 | zscore | bi | 1h | BTC | 2025-H1 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 746 | T3 | T3-ZS-30-2.5-BTC-2025-H2 | zscore | bi | 1h | BTC | 2025-H2 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 747 | T3 | T3-ZS-30-2.5-ETH-2024-H2 | zscore | bi | 1h | ETH | 2024-H2 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 748 | T3 | T3-ZS-30-2.5-ETH-2025-H1 | zscore | bi | 1h | ETH | 2025-H1 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 749 | T3 | T3-ZS-30-2.5-ETH-2025-H2 | zscore | bi | 1h | ETH | 2025-H2 | none | window=30,threshold=2.5 | 8% | zscore param reabertura 1h thresholds restritivos |
| 750 | T3 | T3-ASSET-v2_bol_long-LINK-2024-H2 | bollinger | long | 1h | LINK | 2024-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 751 | T3 | T3-ASSET-v2_bol_long-LINK-2025-H1 | bollinger | long | 1h | LINK | 2025-H1 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 752 | T3 | T3-ASSET-v2_bol_long-LINK-2025-H2 | bollinger | long | 1h | LINK | 2025-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 753 | T3 | T3-ASSET-v2_bol_long-DOT-2024-H2 | bollinger | long | 1h | DOT | 2024-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 754 | T3 | T3-ASSET-v2_bol_long-DOT-2025-H1 | bollinger | long | 1h | DOT | 2025-H1 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 755 | T3 | T3-ASSET-v2_bol_long-DOT-2025-H2 | bollinger | long | 1h | DOT | 2025-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 756 | T3 | T3-ASSET-v2_bol_long-AVAX-2024-H2 | bollinger | long | 1h | AVAX | 2024-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 757 | T3 | T3-ASSET-v2_bol_long-AVAX-2025-H1 | bollinger | long | 1h | AVAX | 2025-H1 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 758 | T3 | T3-ASSET-v2_bol_long-AVAX-2025-H2 | bollinger | long | 1h | AVAX | 2025-H2 | stack_canonical | window=30,num_std=1.5 | 15% | asset expansion stack top combos (requires ingest) |
| 759 | T3 | T3-ASSET-v3_rsi_short_width-LINK-2024-H2 | rsi | short | 1h | LINK | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 760 | T3 | T3-ASSET-v3_rsi_short_width-LINK-2025-H1 | rsi | short | 1h | LINK | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 761 | T3 | T3-ASSET-v3_rsi_short_width-LINK-2025-H2 | rsi | short | 1h | LINK | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 762 | T3 | T3-ASSET-v3_rsi_short_width-DOT-2024-H2 | rsi | short | 1h | DOT | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 763 | T3 | T3-ASSET-v3_rsi_short_width-DOT-2025-H1 | rsi | short | 1h | DOT | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 764 | T3 | T3-ASSET-v3_rsi_short_width-DOT-2025-H2 | rsi | short | 1h | DOT | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 765 | T3 | T3-ASSET-v3_rsi_short_width-AVAX-2024-H2 | rsi | short | 1h | AVAX | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 766 | T3 | T3-ASSET-v3_rsi_short_width-AVAX-2025-H1 | rsi | short | 1h | AVAX | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 767 | T3 | T3-ASSET-v3_rsi_short_width-AVAX-2025-H2 | rsi | short | 1h | AVAX | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 768 | T3 | T3-ASSET-v7_rsi_long_width-LINK-2024-H2 | rsi | long | 1h | LINK | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 769 | T3 | T3-ASSET-v7_rsi_long_width-LINK-2025-H1 | rsi | long | 1h | LINK | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 770 | T3 | T3-ASSET-v7_rsi_long_width-LINK-2025-H2 | rsi | long | 1h | LINK | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 771 | T3 | T3-ASSET-v7_rsi_long_width-DOT-2024-H2 | rsi | long | 1h | DOT | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 772 | T3 | T3-ASSET-v7_rsi_long_width-DOT-2025-H1 | rsi | long | 1h | DOT | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 773 | T3 | T3-ASSET-v7_rsi_long_width-DOT-2025-H2 | rsi | long | 1h | DOT | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 774 | T3 | T3-ASSET-v7_rsi_long_width-AVAX-2024-H2 | rsi | long | 1h | AVAX | 2024-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 775 | T3 | T3-ASSET-v7_rsi_long_width-AVAX-2025-H1 | rsi | long | 1h | AVAX | 2025-H1 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 776 | T3 | T3-ASSET-v7_rsi_long_width-AVAX-2025-H2 | rsi | long | 1h | AVAX | 2025-H2 | stack_canonical | period=14,os=30,ob=70 | 15% | asset expansion stack top combos (requires ingest) |
| 777 | T3 | T3-ASSET-v6_rsi_short_trendhtf-LINK-2024-H2 | rsi | short | 1h | LINK | 2024-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 778 | T3 | T3-ASSET-v6_rsi_short_trendhtf-LINK-2025-H1 | rsi | short | 1h | LINK | 2025-H1 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 779 | T3 | T3-ASSET-v6_rsi_short_trendhtf-LINK-2025-H2 | rsi | short | 1h | LINK | 2025-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 780 | T3 | T3-ASSET-v6_rsi_short_trendhtf-DOT-2024-H2 | rsi | short | 1h | DOT | 2024-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 781 | T3 | T3-ASSET-v6_rsi_short_trendhtf-DOT-2025-H1 | rsi | short | 1h | DOT | 2025-H1 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 782 | T3 | T3-ASSET-v6_rsi_short_trendhtf-DOT-2025-H2 | rsi | short | 1h | DOT | 2025-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 783 | T3 | T3-ASSET-v6_rsi_short_trendhtf-AVAX-2024-H2 | rsi | short | 1h | AVAX | 2024-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 784 | T3 | T3-ASSET-v6_rsi_short_trendhtf-AVAX-2025-H1 | rsi | short | 1h | AVAX | 2025-H1 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 785 | T3 | T3-ASSET-v6_rsi_short_trendhtf-AVAX-2025-H2 | rsi | short | 1h | AVAX | 2025-H2 | stack_canonical | period=14,os=25,ob=75 | 15% | asset expansion stack top combos (requires ingest) |
| 786 | T4 | T4-STRESS-fee+50-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+50 | 40% | adversarial stress scenarios on stack |
| 787 | T4 | T4-STRESS-fee+50-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+50 | 40% | adversarial stress scenarios on stack |
| 788 | T4 | T4-STRESS-fee+50-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+50 | 40% | adversarial stress scenarios on stack |
| 789 | T4 | T4-STRESS-fee+50-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+50 | 40% | adversarial stress scenarios on stack |
| 790 | T4 | T4-STRESS-fee+50-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+50 | 40% | adversarial stress scenarios on stack |
| 791 | T4 | T4-STRESS-fee+100-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+100 | 40% | adversarial stress scenarios on stack |
| 792 | T4 | T4-STRESS-fee+100-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+100 | 40% | adversarial stress scenarios on stack |
| 793 | T4 | T4-STRESS-fee+100-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+100 | 40% | adversarial stress scenarios on stack |
| 794 | T4 | T4-STRESS-fee+100-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+100 | 40% | adversarial stress scenarios on stack |
| 795 | T4 | T4-STRESS-fee+100-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fee+100 | 40% | adversarial stress scenarios on stack |
| 796 | T4 | T4-STRESS-spread+20-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=spread+20 | 40% | adversarial stress scenarios on stack |
| 797 | T4 | T4-STRESS-spread+20-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=spread+20 | 40% | adversarial stress scenarios on stack |
| 798 | T4 | T4-STRESS-spread+20-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=spread+20 | 40% | adversarial stress scenarios on stack |
| 799 | T4 | T4-STRESS-spread+20-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=spread+20 | 40% | adversarial stress scenarios on stack |
| 800 | T4 | T4-STRESS-spread+20-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=spread+20 | 40% | adversarial stress scenarios on stack |
| 801 | T4 | T4-STRESS-slippage+100-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=slippage+100 | 40% | adversarial stress scenarios on stack |
| 802 | T4 | T4-STRESS-slippage+100-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=slippage+100 | 40% | adversarial stress scenarios on stack |
| 803 | T4 | T4-STRESS-slippage+100-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=slippage+100 | 40% | adversarial stress scenarios on stack |
| 804 | T4 | T4-STRESS-slippage+100-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=slippage+100 | 40% | adversarial stress scenarios on stack |
| 805 | T4 | T4-STRESS-slippage+100-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=slippage+100 | 40% | adversarial stress scenarios on stack |
| 806 | T4 | T4-STRESS-latency+2bar_delay-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=latency+2bar_delay | 40% | adversarial stress scenarios on stack |
| 807 | T4 | T4-STRESS-latency+2bar_delay-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=latency+2bar_delay | 40% | adversarial stress scenarios on stack |
| 808 | T4 | T4-STRESS-latency+2bar_delay-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=latency+2bar_delay | 40% | adversarial stress scenarios on stack |
| 809 | T4 | T4-STRESS-latency+2bar_delay-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=latency+2bar_delay | 40% | adversarial stress scenarios on stack |
| 810 | T4 | T4-STRESS-latency+2bar_delay-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=latency+2bar_delay | 40% | adversarial stress scenarios on stack |
| 811 | T4 | T4-STRESS-gap_injection_5pct-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=gap_injection_5pct | 40% | adversarial stress scenarios on stack |
| 812 | T4 | T4-STRESS-gap_injection_5pct-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=gap_injection_5pct | 40% | adversarial stress scenarios on stack |
| 813 | T4 | T4-STRESS-gap_injection_5pct-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=gap_injection_5pct | 40% | adversarial stress scenarios on stack |
| 814 | T4 | T4-STRESS-gap_injection_5pct-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=gap_injection_5pct | 40% | adversarial stress scenarios on stack |
| 815 | T4 | T4-STRESS-gap_injection_5pct-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=gap_injection_5pct | 40% | adversarial stress scenarios on stack |
| 816 | T4 | T4-STRESS-fill_drop_10pct-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fill_drop_10pct | 40% | adversarial stress scenarios on stack |
| 817 | T4 | T4-STRESS-fill_drop_10pct-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fill_drop_10pct | 40% | adversarial stress scenarios on stack |
| 818 | T4 | T4-STRESS-fill_drop_10pct-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fill_drop_10pct | 40% | adversarial stress scenarios on stack |
| 819 | T4 | T4-STRESS-fill_drop_10pct-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fill_drop_10pct | 40% | adversarial stress scenarios on stack |
| 820 | T4 | T4-STRESS-fill_drop_10pct-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=fill_drop_10pct | 40% | adversarial stress scenarios on stack |
| 821 | T4 | T4-STRESS-regime_shift_midfold-combo1 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=regime_shift_midfold | 40% | adversarial stress scenarios on stack |
| 822 | T4 | T4-STRESS-regime_shift_midfold-combo2 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=regime_shift_midfold | 40% | adversarial stress scenarios on stack |
| 823 | T4 | T4-STRESS-regime_shift_midfold-combo3 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=regime_shift_midfold | 40% | adversarial stress scenarios on stack |
| 824 | T4 | T4-STRESS-regime_shift_midfold-combo4 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=regime_shift_midfold | 40% | adversarial stress scenarios on stack |
| 825 | T4 | T4-STRESS-regime_shift_midfold-combo5 | stack_combo | n/a | 1h | BTC | 2024-H2 | n/a | stress=regime_shift_midfold | 40% | adversarial stress scenarios on stack |
| 826 | T4 | T4-ABL-no_width-BTC-2024-H2 | stack_combo | n/a | 1h | BTC | 2024-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 827 | T4 | T4-ABL-no_width-BTC-2025-H1 | stack_combo | n/a | 1h | BTC | 2025-H1 | ablation_no_width | canonical | 15% | ablation filter components |
| 828 | T4 | T4-ABL-no_width-BTC-2025-H2 | stack_combo | n/a | 1h | BTC | 2025-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 829 | T4 | T4-ABL-no_width-ETH-2024-H2 | stack_combo | n/a | 1h | ETH | 2024-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 830 | T4 | T4-ABL-no_width-ETH-2025-H1 | stack_combo | n/a | 1h | ETH | 2025-H1 | ablation_no_width | canonical | 15% | ablation filter components |
| 831 | T4 | T4-ABL-no_width-ETH-2025-H2 | stack_combo | n/a | 1h | ETH | 2025-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 832 | T4 | T4-ABL-no_width-SOL-2024-H2 | stack_combo | n/a | 1h | SOL | 2024-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 833 | T4 | T4-ABL-no_width-SOL-2025-H1 | stack_combo | n/a | 1h | SOL | 2025-H1 | ablation_no_width | canonical | 15% | ablation filter components |
| 834 | T4 | T4-ABL-no_width-SOL-2025-H2 | stack_combo | n/a | 1h | SOL | 2025-H2 | ablation_no_width | canonical | 15% | ablation filter components |
| 835 | T4 | T4-ABL-no_trend_htf-BTC-2024-H2 | stack_combo | n/a | 1h | BTC | 2024-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 836 | T4 | T4-ABL-no_trend_htf-BTC-2025-H1 | stack_combo | n/a | 1h | BTC | 2025-H1 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 837 | T4 | T4-ABL-no_trend_htf-BTC-2025-H2 | stack_combo | n/a | 1h | BTC | 2025-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 838 | T4 | T4-ABL-no_trend_htf-ETH-2024-H2 | stack_combo | n/a | 1h | ETH | 2024-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 839 | T4 | T4-ABL-no_trend_htf-ETH-2025-H1 | stack_combo | n/a | 1h | ETH | 2025-H1 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 840 | T4 | T4-ABL-no_trend_htf-ETH-2025-H2 | stack_combo | n/a | 1h | ETH | 2025-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 841 | T4 | T4-ABL-no_trend_htf-SOL-2024-H2 | stack_combo | n/a | 1h | SOL | 2024-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 842 | T4 | T4-ABL-no_trend_htf-SOL-2025-H1 | stack_combo | n/a | 1h | SOL | 2025-H1 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 843 | T4 | T4-ABL-no_trend_htf-SOL-2025-H2 | stack_combo | n/a | 1h | SOL | 2025-H2 | ablation_no_trend_htf | canonical | 15% | ablation filter components |
| 844 | T4 | T4-ABL-no_filter-BTC-2024-H2 | stack_combo | n/a | 1h | BTC | 2024-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 845 | T4 | T4-ABL-no_filter-BTC-2025-H1 | stack_combo | n/a | 1h | BTC | 2025-H1 | ablation_no_filter | canonical | 15% | ablation filter components |
| 846 | T4 | T4-ABL-no_filter-BTC-2025-H2 | stack_combo | n/a | 1h | BTC | 2025-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 847 | T4 | T4-ABL-no_filter-ETH-2024-H2 | stack_combo | n/a | 1h | ETH | 2024-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 848 | T4 | T4-ABL-no_filter-ETH-2025-H1 | stack_combo | n/a | 1h | ETH | 2025-H1 | ablation_no_filter | canonical | 15% | ablation filter components |
| 849 | T4 | T4-ABL-no_filter-ETH-2025-H2 | stack_combo | n/a | 1h | ETH | 2025-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 850 | T4 | T4-ABL-no_filter-SOL-2024-H2 | stack_combo | n/a | 1h | SOL | 2024-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 851 | T4 | T4-ABL-no_filter-SOL-2025-H1 | stack_combo | n/a | 1h | SOL | 2025-H1 | ablation_no_filter | canonical | 15% | ablation filter components |
| 852 | T4 | T4-ABL-no_filter-SOL-2025-H2 | stack_combo | n/a | 1h | SOL | 2025-H2 | ablation_no_filter | canonical | 15% | ablation filter components |
| 853 | T4 | T4-ABL-tight_width-BTC-2024-H2 | stack_combo | n/a | 1h | BTC | 2024-H2 | ablation_tight_width | canonical | 15% | ablation filter components |
| 854 | T4 | T4-ABL-tight_width-BTC-2025-H1 | stack_combo | n/a | 1h | BTC | 2025-H1 | ablation_tight_width | canonical | 15% | ablation filter components |
| 855 | T4 | T4-ABL-tight_width-BTC-2025-H2 | stack_combo | n/a | 1h | BTC | 2025-H2 | ablation_tight_width | canonical | 15% | ablation filter components |
| 856 | T4 | T4-EXO-rsi_divergence-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 857 | T4 | T4-EXO-rsi_divergence-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 858 | T4 | T4-EXO-rsi_divergence-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 859 | T4 | T4-EXO-rsi_divergence-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 860 | T4 | T4-EXO-rsi_divergence-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 861 | T4 | T4-EXO-rsi_divergence-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 862 | T4 | T4-EXO-rsi_divergence-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 863 | T4 | T4-EXO-rsi_divergence-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 864 | T4 | T4-EXO-rsi_divergence-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=rsi_divergence | 5% | exotic exploratory: rsi_divergence (requires new code) |
| 865 | T4 | T4-EXO-volume_weighted_bb-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 866 | T4 | T4-EXO-volume_weighted_bb-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 867 | T4 | T4-EXO-volume_weighted_bb-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 868 | T4 | T4-EXO-volume_weighted_bb-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 869 | T4 | T4-EXO-volume_weighted_bb-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 870 | T4 | T4-EXO-volume_weighted_bb-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 871 | T4 | T4-EXO-volume_weighted_bb-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 872 | T4 | T4-EXO-volume_weighted_bb-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 873 | T4 | T4-EXO-volume_weighted_bb-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=volume_weighted_bb | 5% | exotic exploratory: volume_weighted_bb (requires new code) |
| 874 | T4 | T4-EXO-cvd_signal-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 875 | T4 | T4-EXO-cvd_signal-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 876 | T4 | T4-EXO-cvd_signal-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 877 | T4 | T4-EXO-cvd_signal-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 878 | T4 | T4-EXO-cvd_signal-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 879 | T4 | T4-EXO-cvd_signal-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 880 | T4 | T4-EXO-cvd_signal-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 881 | T4 | T4-EXO-cvd_signal-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 882 | T4 | T4-EXO-cvd_signal-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=cvd_signal | 5% | exotic exploratory: cvd_signal (requires new code) |
| 883 | T4 | T4-EXO-funding_rate_fade-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 884 | T4 | T4-EXO-funding_rate_fade-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 885 | T4 | T4-EXO-funding_rate_fade-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 886 | T4 | T4-EXO-funding_rate_fade-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 887 | T4 | T4-EXO-funding_rate_fade-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 888 | T4 | T4-EXO-funding_rate_fade-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 889 | T4 | T4-EXO-funding_rate_fade-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 890 | T4 | T4-EXO-funding_rate_fade-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 891 | T4 | T4-EXO-funding_rate_fade-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=funding_rate_fade | 5% | exotic exploratory: funding_rate_fade (requires new code) |
| 892 | T4 | T4-EXO-open_interest_shift-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 893 | T4 | T4-EXO-open_interest_shift-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 894 | T4 | T4-EXO-open_interest_shift-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 895 | T4 | T4-EXO-open_interest_shift-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 896 | T4 | T4-EXO-open_interest_shift-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 897 | T4 | T4-EXO-open_interest_shift-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 898 | T4 | T4-EXO-open_interest_shift-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 899 | T4 | T4-EXO-open_interest_shift-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 900 | T4 | T4-EXO-open_interest_shift-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=open_interest_shift | 5% | exotic exploratory: open_interest_shift (requires new code) |
| 901 | T4 | T4-EXO-orderbook_imbalance-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 902 | T4 | T4-EXO-orderbook_imbalance-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 903 | T4 | T4-EXO-orderbook_imbalance-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 904 | T4 | T4-EXO-orderbook_imbalance-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 905 | T4 | T4-EXO-orderbook_imbalance-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 906 | T4 | T4-EXO-orderbook_imbalance-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 907 | T4 | T4-EXO-orderbook_imbalance-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 908 | T4 | T4-EXO-orderbook_imbalance-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 909 | T4 | T4-EXO-orderbook_imbalance-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=orderbook_imbalance | 5% | exotic exploratory: orderbook_imbalance (requires new code) |
| 910 | T4 | T4-EXO-bid_ask_spread_shift-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 911 | T4 | T4-EXO-bid_ask_spread_shift-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 912 | T4 | T4-EXO-bid_ask_spread_shift-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 913 | T4 | T4-EXO-bid_ask_spread_shift-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 914 | T4 | T4-EXO-bid_ask_spread_shift-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 915 | T4 | T4-EXO-bid_ask_spread_shift-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 916 | T4 | T4-EXO-bid_ask_spread_shift-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 917 | T4 | T4-EXO-bid_ask_spread_shift-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 918 | T4 | T4-EXO-bid_ask_spread_shift-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=bid_ask_spread_shift | 5% | exotic exploratory: bid_ask_spread_shift (requires new code) |
| 919 | T4 | T4-EXO-session_of_day_bias-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 920 | T4 | T4-EXO-session_of_day_bias-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 921 | T4 | T4-EXO-session_of_day_bias-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 922 | T4 | T4-EXO-session_of_day_bias-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 923 | T4 | T4-EXO-session_of_day_bias-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 924 | T4 | T4-EXO-session_of_day_bias-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 925 | T4 | T4-EXO-session_of_day_bias-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 926 | T4 | T4-EXO-session_of_day_bias-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 927 | T4 | T4-EXO-session_of_day_bias-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=session_of_day_bias | 5% | exotic exploratory: session_of_day_bias (requires new code) |
| 928 | T4 | T4-EXO-day_of_week_bias-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 929 | T4 | T4-EXO-day_of_week_bias-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 930 | T4 | T4-EXO-day_of_week_bias-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 931 | T4 | T4-EXO-day_of_week_bias-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 932 | T4 | T4-EXO-day_of_week_bias-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 933 | T4 | T4-EXO-day_of_week_bias-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 934 | T4 | T4-EXO-day_of_week_bias-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 935 | T4 | T4-EXO-day_of_week_bias-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 936 | T4 | T4-EXO-day_of_week_bias-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=day_of_week_bias | 5% | exotic exploratory: day_of_week_bias (requires new code) |
| 937 | T4 | T4-EXO-liquidation_cascade_fade-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 938 | T4 | T4-EXO-liquidation_cascade_fade-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 939 | T4 | T4-EXO-liquidation_cascade_fade-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 940 | T4 | T4-EXO-liquidation_cascade_fade-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 941 | T4 | T4-EXO-liquidation_cascade_fade-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 942 | T4 | T4-EXO-liquidation_cascade_fade-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 943 | T4 | T4-EXO-liquidation_cascade_fade-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 944 | T4 | T4-EXO-liquidation_cascade_fade-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 945 | T4 | T4-EXO-liquidation_cascade_fade-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=liquidation_cascade_fade | 5% | exotic exploratory: liquidation_cascade_fade (requires new c |
| 946 | T4 | T4-EXO-vwap_mean_revert-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 947 | T4 | T4-EXO-vwap_mean_revert-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 948 | T4 | T4-EXO-vwap_mean_revert-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 949 | T4 | T4-EXO-vwap_mean_revert-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 950 | T4 | T4-EXO-vwap_mean_revert-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 951 | T4 | T4-EXO-vwap_mean_revert-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 952 | T4 | T4-EXO-vwap_mean_revert-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 953 | T4 | T4-EXO-vwap_mean_revert-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 954 | T4 | T4-EXO-vwap_mean_revert-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=vwap_mean_revert | 5% | exotic exploratory: vwap_mean_revert (requires new code) |
| 955 | T4 | T4-EXO-price_action_pinbar-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 956 | T4 | T4-EXO-price_action_pinbar-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 957 | T4 | T4-EXO-price_action_pinbar-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 958 | T4 | T4-EXO-price_action_pinbar-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 959 | T4 | T4-EXO-price_action_pinbar-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 960 | T4 | T4-EXO-price_action_pinbar-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 961 | T4 | T4-EXO-price_action_pinbar-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 962 | T4 | T4-EXO-price_action_pinbar-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 963 | T4 | T4-EXO-price_action_pinbar-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=price_action_pinbar | 5% | exotic exploratory: price_action_pinbar (requires new code) |
| 964 | T4 | T4-EXO-breakout_false_fade-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 965 | T4 | T4-EXO-breakout_false_fade-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 966 | T4 | T4-EXO-breakout_false_fade-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 967 | T4 | T4-EXO-breakout_false_fade-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 968 | T4 | T4-EXO-breakout_false_fade-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 969 | T4 | T4-EXO-breakout_false_fade-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 970 | T4 | T4-EXO-breakout_false_fade-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 971 | T4 | T4-EXO-breakout_false_fade-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 972 | T4 | T4-EXO-breakout_false_fade-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=breakout_false_fade | 5% | exotic exploratory: breakout_false_fade (requires new code) |
| 973 | T4 | T4-EXO-gap_fill_intraday-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 974 | T4 | T4-EXO-gap_fill_intraday-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 975 | T4 | T4-EXO-gap_fill_intraday-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 976 | T4 | T4-EXO-gap_fill_intraday-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 977 | T4 | T4-EXO-gap_fill_intraday-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 978 | T4 | T4-EXO-gap_fill_intraday-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 979 | T4 | T4-EXO-gap_fill_intraday-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 980 | T4 | T4-EXO-gap_fill_intraday-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 981 | T4 | T4-EXO-gap_fill_intraday-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=gap_fill_intraday | 5% | exotic exploratory: gap_fill_intraday (requires new code) |
| 982 | T4 | T4-EXO-overnight_holding_bias-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 983 | T4 | T4-EXO-overnight_holding_bias-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 984 | T4 | T4-EXO-overnight_holding_bias-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 985 | T4 | T4-EXO-overnight_holding_bias-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 986 | T4 | T4-EXO-overnight_holding_bias-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 987 | T4 | T4-EXO-overnight_holding_bias-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 988 | T4 | T4-EXO-overnight_holding_bias-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 989 | T4 | T4-EXO-overnight_holding_bias-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 990 | T4 | T4-EXO-overnight_holding_bias-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=overnight_holding_bias | 5% | exotic exploratory: overnight_holding_bias (requires new cod |
| 991 | T4 | T4-EXO-round_number_pin-BTC-2024-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2024-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 992 | T4 | T4-EXO-round_number_pin-BTC-2025-H1 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H1 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 993 | T4 | T4-EXO-round_number_pin-BTC-2025-H2 | exotic_feature_flag | exploratory | 1h | BTC | 2025-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 994 | T4 | T4-EXO-round_number_pin-ETH-2024-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2024-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 995 | T4 | T4-EXO-round_number_pin-ETH-2025-H1 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H1 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 996 | T4 | T4-EXO-round_number_pin-ETH-2025-H2 | exotic_feature_flag | exploratory | 1h | ETH | 2025-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 997 | T4 | T4-EXO-round_number_pin-SOL-2024-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2024-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 998 | T4 | T4-EXO-round_number_pin-SOL-2025-H1 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H1 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 999 | T4 | T4-EXO-round_number_pin-SOL-2025-H2 | exotic_feature_flag | exploratory | 1h | SOL | 2025-H2 | none | feature=round_number_pin | 5% | exotic exploratory: round_number_pin (requires new code) |
| 1000 | T4 | T4-ML-ols_mean_reverting_residual-BTC-2024-H2 | ml_feature_flag | adaptive | 1h | BTC | 2024-H2 | none | method=ols_mean_reverting_residual | 5% | ML/stat experiment ols_mean_reverting_residual (requires new |

# SPEC.md - AZ.3 bollinger 30/1.5 BTC 1h 2025-H1 + bollinger_width:250

> Gate: **pesquisa**. Serie AZ.

## Hipotese

BTC 30/1.5 long_only + bollinger_width:250 em 2025-H1. Serie AZ formaliza achado da exploracao AL-AY: strategy window=30 Pareto-domina w=20 em MDD e min p5 cross-year. bollinger_width:250 w=20 ns=2.0 e o filtro de regime com menor MDD cross-window. Piloto passa ALL strict gates (p5>=10000, mdd p95<=10%, ratio>=0.95, fee==spread).

## Mercado

btcusdt_1h_20250105_20250704_binance_spot, ~4320 barras 1h.

## Entradas

BollingerMeanReversionStrategy(window=30, num_std=1.5) causal, edge-triggered, long_only + bollinger_width:window=20:num_std=2.0:min_width_bps=250.

## Saidas

Edge-triggered mean-reversion. Custos H.1 (taker_fee_bps=5, slippage_bps_per_unit_notional=10).

## Criterio

ADR-0025 hibrido + strict tail gate (p5 MC >= 10000).

## Familia de filtro

bollinger_width (Serie AK - 3a familia ortogonal ao atr_regime). Parametros BW canonicos (melhor Pareto em AM).

## Motivacao AZ vs AK

AK usava strategy w=20. AZ usa strategy w=30 (Pareto-otima em AW+AX). Gera 4/14 pilotos ALL-gates-pass vs 2/8 AK.

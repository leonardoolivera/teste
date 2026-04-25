# IMPLEMENTATION.md - AD.1

> Gate: **implementação**.

Zero código novo. Reuso de ADR-0026 (Bollinger) + ADR-0023 (ATRRegimeFilter, onde aplicável).

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id btcusdt_1h_20250705_20251231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=55 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-btc-1h-2025-regime-atr-55 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: BollingerMeanReversionStrategy(window=20, num_std=1.5, long_only=True)
- Filtro: atr_regime:window=14:min_atr_bps=55
- Dataset: btcusdt_1h_20250705_20251231_binance_spot (4320 barras)

## Gap de código

Nenhum. ADR-0026 + ADR-0022 suportam combinação 20/1.5 + ATR.

## Arquivos alterados

Nenhum em `src/` ou `tests/` (reuso puro).

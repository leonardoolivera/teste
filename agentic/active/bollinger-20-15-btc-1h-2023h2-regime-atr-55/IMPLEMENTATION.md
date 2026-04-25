# IMPLEMENTATION.md - AH.2

> Gate: **implementação**. Zero código novo.

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id btcusdt_1h_20230705_20231231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=55 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-btc-1h-2023h2-regime-atr-55 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: Bollinger 20/1.5
- Filtro: atr_regime:window=14:min_atr_bps=55
- Dataset: btcusdt_1h_20230705_20231231_binance_spot

## Arquivos alterados

Nenhum. 3 datasets 2023-H2 ingeridos hoje; dataset ETH 4h reusado.

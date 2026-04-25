# IMPLEMENTATION.md - AH.3

> Gate: **implementação**. Zero código novo.

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id solusdt_1h_20230705_20231231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=100 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-sol-1h-2023h2-regime-atr-100 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: Bollinger 20/1.5
- Filtro: atr_regime:window=14:min_atr_bps=100
- Dataset: solusdt_1h_20230705_20231231_binance_spot

## Arquivos alterados

Nenhum. 3 datasets 2023-H2 ingeridos hoje; dataset ETH 4h reusado.

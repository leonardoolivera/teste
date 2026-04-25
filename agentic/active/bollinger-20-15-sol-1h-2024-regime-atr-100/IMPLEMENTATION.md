# IMPLEMENTATION.md - AE.2

> Gate: **implementação**.

Zero código novo. Reuso de ADR-0026 + ADR-0022.

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id solusdt_1h_20240705_20241231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=100 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-sol-1h-2024-regime-atr-100 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: BollingerMeanReversionStrategy(window=20, num_std=1.5, long_only=True)
- Filtro: atr_regime:window=14:min_atr_bps=100
- Dataset: solusdt_1h_20240705_20241231_binance_spot

## Arquivos alterados

Nenhum em `src/` ou `tests/`.

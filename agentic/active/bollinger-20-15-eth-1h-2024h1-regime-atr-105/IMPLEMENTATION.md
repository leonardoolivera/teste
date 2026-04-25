# IMPLEMENTATION.md - AG.1

> Gate: **implementação**.

Zero código novo.

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id ethusdt_1h_20240105_20240704_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=105 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-eth-1h-2024h1-regime-atr-105 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: BollingerMeanReversionStrategy(window=20, num_std=1.5)
- Filtro: atr_regime:window=14:min_atr_bps=105
- Dataset: ethusdt_1h_20240105_20240704_binance_spot (4368 barras, 2024-01-05 a 2024-07-04)

## Arquivos alterados

Nenhum em `src/` ou `tests/`. `data/datasets.yaml` ganhou 3 entradas hoje (BTC/ETH/SOL 2024-H1).

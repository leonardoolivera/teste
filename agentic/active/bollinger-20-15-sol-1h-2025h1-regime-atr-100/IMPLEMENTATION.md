# IMPLEMENTATION.md - AF.3

> Gate: **implementação**.

Zero código novo. Primeira vez usando dataset solusdt_1h_20250105_20250704_binance_spot (ingesta nova hoje).

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id solusdt_1h_20250105_20250704_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=100 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-sol-1h-2025h1-regime-atr-100 --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: BollingerMeanReversionStrategy(window=20, num_std=1.5)
- Filtro: atr_regime:window=14:min_atr_bps=100
- Dataset: solusdt_1h_20250105_20250704_binance_spot (4344 barras, ingesta 2025-01-05 to 2025-07-04)

## Arquivos alterados

Nenhum em `src/` ou `tests/`. `data/datasets.yaml` ganhou 3 entradas hoje (BTC/ETH/SOL 2025-H1).

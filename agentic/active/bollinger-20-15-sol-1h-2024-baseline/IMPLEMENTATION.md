# IMPLEMENTATION.md - AE.4

> Gate: **implementação**.

Zero código novo. Reuso de ADR-0026 + ADR-0022.

## CLI executado

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 1.5 --dataset-id solusdt_1h_20240705_20241231_binance_spot  --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-15-sol-1h-2024-baseline --mc-seed 42 --mc-resamples 1000`

## Mapeamento SPEC → execução

- Estratégia: BollingerMeanReversionStrategy(window=20, num_std=1.5, long_only=True)
- Filtro: nenhum (controle)
- Dataset: solusdt_1h_20240705_20241231_binance_spot

## Arquivos alterados

Nenhum em `src/` ou `tests/`.

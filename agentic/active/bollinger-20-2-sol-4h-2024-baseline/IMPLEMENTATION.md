# IMPLEMENTATION.md — M.1 Bollinger 20/2 SOL 4h 2024

## Dependências

Reuso puro. Zero código novo. `TIMEFRAME_DELTAS` já tem `4h` desde entregas iniciais.

## Arquivos alterados (por este piloto)

- `data/datasets.yaml` — manifesto `solusdt_4h_20240705_20241231_binance_spot` (sha256=`04a5a335`).

## Mapeamento SPEC → execução

- SPEC §1 → `alpha-forge validate` sobre `solusdt_4h_20240705_20241231_binance_spot`.
- SPEC §4-5 → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- `--min-test-bars 50` (baixo, para acomodar 1080 barras / 4 folds ≈ 270 barras de teste).

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-sol-4h-2024-baseline \
  --dataset-id solusdt_4h_20240705_20241231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

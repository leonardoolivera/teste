# IMPLEMENTATION.md — M.2 Bollinger 20/2 BTC 4h 2024

## Dependências

Reuso puro.

## Arquivos alterados (por este piloto)

- `data/datasets.yaml` — manifesto `btcusdt_4h_20240705_20241231_binance_spot` (sha256=`2b1256ea`).

## Mapeamento SPEC → execução

- SPEC §1 → `alpha-forge validate` sobre `btcusdt_4h_20240705_20241231_binance_spot`.
- SPEC §4-5 → `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only`.
- `--min-test-bars 50`.

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-btc-4h-2024-baseline \
  --dataset-id btcusdt_4h_20240705_20241231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

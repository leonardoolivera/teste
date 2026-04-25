# IMPLEMENTATION.md — I.2 Bollinger 20/2 BTC 180d

## Dependências

Reuso puro de ADR-0026 + CLI `bollinger` (entregues em I.1). Zero código novo.

## Arquivos alterados

- `agentic/active/bollinger-20-2-btc-180d-baseline/*.md` + `results/validation/bollinger-20-2-btc-180d-baseline/*.json`.

## Mapeamento SPEC

| SPEC §          | Implementação                                                   |
| --------------- | --------------------------------------------------------------- |
| §2 BTC          | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot`        |
| §4-5 Boll 20/2  | `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only` |
| §9 custos H.1   | `--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0` |

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-btc-180d-baseline \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

Executado em `2026-04-18T10:33:04Z`.

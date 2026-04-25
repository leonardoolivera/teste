# IMPLEMENTATION.md — H.8 Donchian 40/20 BTC 180d

## Dependências

Reuso puro; nenhum código novo.

## Arquivos alterados

- `agentic/active/donchian-40-20-btc-180d-baseline/*.md` (6 artefatos).
- `results/validation/donchian-40-20-btc-180d-baseline/*.json` (4 artefatos CLI).
- `STATE.md` (Frente H.8).

## Mapeamento SPEC

| SPEC §      | Implementação              |
| ----------- | -------------------------- |
| §4 entry 40 | `--entry-window 40`        |
| §5 exit 20  | `--exit-window 20`         |
| §2 BTC      | dataset BTCUSDT 1h 180d    |
| §6-11-bis   | custos H.1; sem filtro     |

## Comando

```bash
alpha-forge validate --run-id donchian-40-20-btc-180d-baseline \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 40 --exit-window 20 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

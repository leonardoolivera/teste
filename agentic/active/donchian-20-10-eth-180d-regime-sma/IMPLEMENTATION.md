# IMPLEMENTATION.md — H.9 Donchian 20/10 ETH 180d + SMA filter

## Dependências

Reuso puro; nenhum código novo.

## Arquivos alterados

- `agentic/active/donchian-20-10-eth-180d-regime-sma/*.md` + `results/validation/donchian-20-10-eth-180d-regime-sma/*.json` + STATE.

## Mapeamento SPEC

| SPEC §       | Implementação                                                        |
| ------------ | -------------------------------------------------------------------- |
| §2 ETH       | `--dataset-id ethusdt_1h_20250705_20251231_binance_spot`             |
| §11-bis SMA  | `--regime-filter sma_slope:window=50:min_slope_bps=10`               |
| §4-5 Don20/10| `--strategy donchian --entry-window 20 --exit-window 10 --long-only` |

## Comando

```bash
alpha-forge validate --run-id donchian-20-10-eth-180d-regime-sma \
  --dataset-id ethusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10 \
  --regime-filter sma_slope:window=50:min_slope_bps=10
```

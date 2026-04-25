# IMPLEMENTATION.md — H.10 Donchian 20/10 SOL 180d

## Dependências

Reuso puro; nenhum código novo.

## Arquivos alterados

- `agentic/active/donchian-20-10-sol-180d-baseline/*.md` + `results/validation/donchian-20-10-sol-180d-baseline/*.json` + STATE.

## Mapeamento SPEC

| SPEC §     | Implementação                                                        |
| ---------- | -------------------------------------------------------------------- |
| §2 SOL     | `--dataset-id solusdt_1h_20250705_20251231_binance_spot`             |
| §4-5 Don20/10 | `--strategy donchian --entry-window 20 --exit-window 10 --long-only` |
| §11-bis none| (sem `--regime-filter`)                                             |

## Comando

```bash
alpha-forge validate --run-id donchian-20-10-sol-180d-baseline \
  --dataset-id solusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

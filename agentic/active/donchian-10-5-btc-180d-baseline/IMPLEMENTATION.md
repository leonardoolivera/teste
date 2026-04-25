# IMPLEMENTATION.md — H.7 Donchian 10/5 BTC 180d

## Dependências

Nenhuma nova; reuso puro de infraestrutura H.1 (Donchian family aceita `entry_window`/`exit_window` como parâmetros).

## Arquivos alterados

Somente artefatos agentic + JSONs:

- `agentic/active/donchian-10-5-btc-180d-baseline/{SPEC,IMPLEMENTATION,VALIDATION,BACKTEST,AUDIT,CHECKLIST}.md`.
- `results/validation/donchian-10-5-btc-180d-baseline/{run,walk_forward,monte_carlo,cost_stress}.json`.
- `STATE.md` (Frente H.7 adicionada).

## Mapeamento SPEC

| SPEC §         | Implementação                                        |
| -------------- | ---------------------------------------------------- |
| §4 entry 10    | `--entry-window 10`                                  |
| §5 exit 5      | `--exit-window 5`                                    |
| §11-bis none   | (sem `--regime-filter`)                              |
| §2 BTC         | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot` |

## Comando

```bash
alpha-forge validate --run-id donchian-10-5-btc-180d-baseline \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 10 --exit-window 5 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

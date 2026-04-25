# IMPLEMENTATION.md — H.6 Donchian + Composite(sma OR atr)

## Dependências

- ADR-0022, ADR-0023 (já entregues); zero código novo neste piloto — reuso puro.

## Arquivos alterados

Apenas artefatos agentic + JSONs gerados pelo CLI:

- `agentic/active/donchian-20-10-btc-180d-regime-sma-or-atr/{SPEC,IMPLEMENTATION,VALIDATION,BACKTEST,AUDIT,CHECKLIST}.md`.
- `results/validation/donchian-20-10-btc-180d-regime-sma-or-atr/{run,walk_forward,monte_carlo,cost_stress}.json`.
- `STATE.md` (Frente H.6 adicionada).

## Mapeamento SPEC

| SPEC §              | Implementação                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| §11-bis Composite OR| `--regime-filter "or(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)"`  |
| §4-5 Donchian 20/10 | `--strategy donchian --entry-window 20 --exit-window 10 --long-only`                              |
| §7 sizing           | `--fracao 0.1 --alavancagem 2.0`                                                                  |
| §8-10 custos        | `--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0`                            |
| §Critério stress    | `--stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10`                          |

## Comando executado

```bash
alpha-forge validate --run-id donchian-20-10-btc-180d-regime-sma-or-atr \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10 \
  --regime-filter "or(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)"
```

Canonical persistido em `run.json.flags.regime_filter` — filtros internos reordenados lex.

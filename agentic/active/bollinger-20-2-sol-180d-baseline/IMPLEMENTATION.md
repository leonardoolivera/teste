# IMPLEMENTATION.md — I.1 Bollinger 20/2 SOL 180d

## Dependências

Código novo **já integrado** ao repositório antes de abrir este piloto:

- `src/alpha_forge/strategies/families/bollinger/{__init__.py,strategy.py}` — `BollingerMeanReversionStrategy`
  (ADR-0026).
- `src/alpha_forge/cli/app.py` — adiciona `"bollinger"` à lista `AVAILABLE_STRATEGIES` + flags
  `--bollinger-window` (default 20) + `--bollinger-num-std` (default 2.0).
- Testes: `tests/unit/test_bollinger_mean_reversion.py` (23) + `tests/property/test_bollinger_causal.py` (1)
  + `tests/property/test_cost_monotonicity_bollinger.py` (1).

Reuso puro para este piloto: engine, walk-forward, Monte Carlo, cost stress, ranking (ADR-0024),
loaders de dataset SOL. Nenhum código específico ao piloto.

## Arquivos alterados (por este piloto)

- `agentic/active/bollinger-20-2-sol-180d-baseline/*.md` — 6 artefatos.
- `results/validation/bollinger-20-2-sol-180d-baseline/{run,walk_forward,monte_carlo,cost_stress}.json` — 4 JSONs.
- `results/ranking/<timestamp>.json` — leaderboard N=13.
- `STATE.md` — Current phase + What was last delivered + Next step.
- `system/api.md` — surface de `--strategy bollinger` + Python API.
- `system/flows.md` — fluxo da família Bollinger.

## Mapeamento SPEC

| SPEC §              | Implementação                                                      |
| ------------------- | ------------------------------------------------------------------ |
| §2 SOL              | `--dataset-id solusdt_1h_20250705_20251231_binance_spot`           |
| §4-5 Bollinger 20/2 | `--strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only` |
| §11-bis none        | (sem `--regime-filter`, default `none`)                            |
| §6 sem stops        | (sem flags de stop; convenção da série)                            |
| §9 custos H.1       | `--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0` |
| §7 sizing           | `--capital 10000 --fracao 0.1 --alavancagem 2.0`                   |

## Comando

```bash
alpha-forge validate --run-id bollinger-20-2-sol-180d-baseline \
  --dataset-id solusdt_1h_20250705_20251231_binance_spot \
  --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10
```

Executado em `2026-04-18T10:21:33Z`. Timestamp em `results/validation/bollinger-20-2-sol-180d-baseline/run.json`.

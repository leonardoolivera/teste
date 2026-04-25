# IMPLEMENTATION.md — H.3 Donchian+regime SMA slope

> Gate ativo: **implementação**. Primeiro consumidor real de ADR-0022 — `src/alpha_forge/regimes/` já existe e foi testado via property-based; este piloto apenas monta o comando canônico.

## Gap de código

**Zero.** ADR-0011 + ADR-0022 + CLI `validate` com `--regime-filter` estão todos em `src/alpha_forge/`. Nenhuma linha de código é adicionada ou modificada neste piloto.

## Arquivos alterados

**Nenhum arquivo em `src/` ou `tests/` alterado por este piloto.** ADR-0022 foi implementada na frente anterior (ver STATE.md "Frente I") — os arquivos relevantes (`src/alpha_forge/regimes/filter.py`, `src/alpha_forge/backtest/engine.py`, `src/alpha_forge/validation/{walk_forward,cost_stress}.py`, `src/alpha_forge/cli/app.py`, 3 tests property + 3 tests integration) já estavam commitados antes deste piloto começar.

Arquivos **criados por este piloto** (apenas artefatos agentic + JSONs de resultados):

- `agentic/active/donchian-20-10-btc-180d-regime-sma/{SPEC,IMPLEMENTATION,VALIDATION,BACKTEST,AUDIT,CHECKLIST}.md`
- `results/validation/donchian-20-10-btc-180d-regime-sma/{run,walk_forward,monte_carlo,cost_stress}.json`

## Mapeamento SPEC → código

| SPEC § | Código |
|---|---|
| §4 Entradas (Donchian breakout long) | [src/alpha_forge/strategies/families/donchian.py](../../../src/alpha_forge/strategies/families/donchian.py) (ADR-0011) |
| §5 Saídas (rompimento-baixo 10) | idem |
| §7 Sizing fracao=0.1 alavancagem=2.0 | [src/alpha_forge/risk/sizing.py](../../../src/alpha_forge/risk/sizing.py) (ADR-0004) |
| §8 Fees taker 5bps | [src/alpha_forge/backtest/cost.py](../../../src/alpha_forge/backtest/cost.py) (ADR-0006) |
| §9 Slippage 2bps/unit_notional | idem |
| §10 Spread 0bps + cost_stress 10bps | idem + [src/alpha_forge/validation/cost_stress.py](../../../src/alpha_forge/validation/cost_stress.py) (ADR-0014 + ADR-0019) |
| **§11-bis Regime filter SMA slope** | [src/alpha_forge/regimes/filter.py::SMASlopeFilter](../../../src/alpha_forge/regimes/filter.py) (ADR-0022) |
| §Critério cost_stress spread+10 | `--stress spread+10:0:0:10` |

## Integração ADR-0022

Engine ([src/alpha_forge/backtest/engine.py](../../../src/alpha_forge/backtest/engine.py) `run_backtest`) avalia `regime_filter.is_active(window)` após `strategy.decide` e antes de sizing. Quando `False`:

- `position.side == FLAT` → `signal = HOLD` (não entra).
- `position.side != FLAT` → `signal = EXIT` (fecha em `t+1 open` com custo normal).

CLI `validate` propaga o filtro para `walk_forward` (por fold) e `cost_stress` (baseline + 3 cenários). Canonicalização alfabética salva em `run.json.flags["regime_filter"] = "sma_slope:min_slope_bps=10:window=50"`.

## Comando canônico

```bash
alpha-forge validate \
  --run-id donchian-20-10-btc-180d-regime-sma \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 \
  --n-folds 5 --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10 \
  --regime-filter sma_slope:window=50:min_slope_bps=10
```

## Comando `compare` (gate 4)

```bash
alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-regime-sma
```

**Expectativa:** exatamente 2 flags divergem (`regime_filter`, `run_id`). Confirmado (ver AUDIT.md).

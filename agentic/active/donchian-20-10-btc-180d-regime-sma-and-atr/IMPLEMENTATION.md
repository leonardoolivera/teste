# IMPLEMENTATION.md — Donchian 20/10 + CompositeFilter(sma_slope AND atr_regime) (H.5)

> Gate: **pesquisa**. Primeiro consumidor real de ADR-0023 (CompositeFilter). Zero tuning: reuso literal de `SMASlopeFilter(window=50, min_slope_bps=10)` (H.3) e `ATRRegimeFilter(window=14, min_atr_bps=50)` (H.4).

## Dependências

- ADR-0020 (5-gate protocol).
- ADR-0022 (RegimeFilter Protocol + canonical parser).
- **ADR-0023 (CompositeFilter AND/OR)** — novo; este piloto é o primeiro consumidor real.
- `alpha_forge.regimes.CompositeFilter`, `SMASlopeFilter`, `ATRRegimeFilter`, `canonical_string`, `parse_spec`.
- CLI `alpha-forge validate --regime-filter "and(...)"` já despacha para `parse_spec` — sem mudanças adicionais.

## Arquivos alterados

Nenhum arquivo de código precisou ser modificado para este piloto — toda a infraestrutura foi entregue por ADR-0022 (H.3) e ADR-0023 (fase anterior a H.5). Somente artefatos agentic:

- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/SPEC.md` (novo).
- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/IMPLEMENTATION.md` (este arquivo).
- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/VALIDATION.md` (próximo).
- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/BACKTEST.md`.
- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/AUDIT.md`.
- `agentic/active/donchian-20-10-btc-180d-regime-sma-and-atr/CHECKLIST.md`.
- `results/validation/donchian-20-10-btc-180d-regime-sma-and-atr/{run,walk_forward,monte_carlo,cost_stress}.json` (gerados pelo CLI).
- `STATE.md` (Frente H.5 adicionado, Next step atualizado).

## Mapeamento SPEC

| SPEC §                     | Implementação                                                                                   |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| §2 Mercado BTCUSDT spot    | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot`                                        |
| §3 Timeframe 1h 180d       | 4320 barras do dataset acima.                                                                   |
| §4 ENTER_LONG rompimento   | `--strategy donchian --entry-window 20`                                                         |
| §5 EXIT rompimento-baixo   | `--exit-window 10`                                                                              |
| §6 Sem stops               | (nenhuma flag de stop).                                                                         |
| §7 fracao=0.1, alav=2.0    | `--fracao 0.1 --alavancagem 2.0`                                                                |
| §8-10 fees/slip/spread     | `--taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0`                          |
| §11 N/A funding (spot)     | (nenhuma flag).                                                                                 |
| §11-bis Composite AND      | `--regime-filter "and(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)"` |
| §12 Warm-up 51             | Gerenciado por `CompositeFilter.is_active` via `max(51,15)`.                                    |
| §Critério stress           | `--stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10`                        |

## Construção do CompositeFilter

```python
from alpha_forge.regimes import (
    ATRRegimeFilter, CompositeFilter, SMASlopeFilter, canonical_string,
)

sma = SMASlopeFilter(window=50, min_slope_bps=10)
atr = ATRRegimeFilter(window=14, min_atr_bps=50)
filt = CompositeFilter([sma, atr], mode="and")

canonical_string(filt)
# 'and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)'
```

## Warm-up efetivo

- `max(SMA warmup=51, ATR warmup=15) = 51 barras causais`.
- Donchian warm-up `entry_window=20` é dominado pelo SMA interno do composto.
- Primeiras 51 barras → `HOLD` forçado.

## Invariantes preservados

- **Causalidade (ADR-0002):** `CompositeFilter.is_active` lê apenas `window.iloc[:-1]`; herdada de cada filtro interno + `all`/`any` determinísticos. Verificado por `test_composite_filter_lookahead.py`.
- **Canonical comutativo (ADR-0023):** ordem dos filtros internos no construtor não muda a string canônica. Verificado por `test_composite_filter_canonical.py`.
- **Roundtrip parse→canonical:** `canonical_string(parse_spec(s)) == s`. Verificado mesmo teste.
- **Sem tuning intra-walk-forward (ADR-0003):** thresholds (slope 10, ATR 50) fixados antes do split; idênticos a H.3 e H.4.

## Comando executado

```bash
alpha-forge validate \
  --run-id donchian-20-10-btc-180d-regime-sma-and-atr \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 --long-only \
  --capital 10000 --fracao 0.1 --alavancagem 2.0 \
  --taker-fee-bps 5.0 --slippage-bps-per-notional 2.0 --spread-bps 0.0 \
  --n-folds 5 --scheme rolling --train-fraction 0.5 --min-test-bars 50 \
  --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10 \
  --regime-filter "and(sma_slope:window=50:min_slope_bps=10,atr_regime:window=14:min_atr_bps=50)"
```

Canonical persistido em `run.json.flags.regime_filter` com filtros reordenados lexicograficamente — `atr_regime` antes de `sma_slope`.

## Gap de código efetivo neste piloto

Zero linhas de produto. Reuso puro. O trabalho aditivo foi absorvido por ADR-0023 na fase anterior:

- `src/alpha_forge/regimes/filter.py` — `CompositeFilter` (~60 linhas).
- `src/alpha_forge/regimes/__init__.py` — export.
- 4 tests property-based (`test_composite_filter_{canonical,lookahead,restrictive}.py`) + 2 CLI tests.
- ADR-0023 documento + índice + `system/api.md`.

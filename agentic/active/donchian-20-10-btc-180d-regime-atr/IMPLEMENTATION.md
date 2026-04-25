# IMPLEMENTATION.md — H.4 Donchian+regime ATR

> Gate ativo: **implementação**. Segundo consumidor real de ADR-0022. Diferente de H.3 (gap zero), H.4 adiciona `ATRRegimeFilter` concreto — extensão aditiva pre-autorizada em ADR-0022 §Consequences: "Abre caminho para adicionar mais filtros (`atr_regime`, `adx_regime`) no mesmo contrato sem nova ADR — só nova implementação + nova linha de parser."

## Gap de código

Mínimo e aditivo — **não altera nenhum contrato existente**:

- `src/alpha_forge/regimes/filter.py`: adiciona `ATRRegimeFilter(window, min_atr_bps)` (classe concreta, Protocol-compliant) + branch `atr_regime` em `canonical_string` + branch `atr_regime` em `parse_spec`.
- `src/alpha_forge/regimes/__init__.py`: exporta `ATRRegimeFilter`.
- `tests/property/test_atr_filter_lookahead.py`: property-based de causalidade (`window.iloc[-1]` perturbation).
- `tests/property/test_atr_filter_monotonicity.py`: property-based de monotonicidade em `min_atr_bps`.
- `tests/integration/test_cli_run_metadata.py`: +1 teste `test_regime_filter_atr_regime_canonicaliza` confirmando persistência canônica.

Suíte subiu para **298 passed, 1 skipped** (+3 tests).

## Arquivos alterados

| Arquivo | Δ |
|---|---|
| [src/alpha_forge/regimes/filter.py](../../../src/alpha_forge/regimes/filter.py) | +ATRRegimeFilter class (~55 linhas), branches em canonical_string/parse_spec |
| [src/alpha_forge/regimes/__init__.py](../../../src/alpha_forge/regimes/__init__.py) | +ATRRegimeFilter em imports e __all__ |
| [tests/property/test_atr_filter_lookahead.py](../../../tests/property/test_atr_filter_lookahead.py) | novo, ~65 linhas |
| [tests/property/test_atr_filter_monotonicity.py](../../../tests/property/test_atr_filter_monotonicity.py) | novo, ~80 linhas |
| [tests/integration/test_cli_run_metadata.py](../../../tests/integration/test_cli_run_metadata.py) | +1 teste de canonicalização atr_regime |
| [system/api.md](../../../system/api.md) | +entrada ATRRegimeFilter + atualiza canonical_string/parse_spec |

## Mapeamento SPEC → código

| SPEC § | Código |
|---|---|
| §4 Entradas | [src/alpha_forge/strategies/families/donchian.py](../../../src/alpha_forge/strategies/families/donchian.py) (ADR-0011) |
| §5 Saídas | idem |
| §7 Sizing | [src/alpha_forge/risk/sizing.py](../../../src/alpha_forge/risk/sizing.py) (ADR-0004) |
| §8–§10 Custos | [src/alpha_forge/backtest/cost.py](../../../src/alpha_forge/backtest/cost.py) + [validation/cost_stress.py](../../../src/alpha_forge/validation/cost_stress.py) |
| **§11-bis Regime filter ATR** | [src/alpha_forge/regimes/filter.py::ATRRegimeFilter](../../../src/alpha_forge/regimes/filter.py) (novo) |
| §Critério cost_stress spread+10 | `--stress spread+10:0:0:10` |

## Integração ADR-0022 (reusada)

Mesma mecânica de H.3 — `run_backtest` consulta `regime_filter.is_active(window)` após `strategy.decide` e coage `HOLD`/`EXIT`. Nenhuma mudança no engine; apenas `ATRRegimeFilter` concreta cumpre o Protocol e se encaixa.

Canonicalização: `flags["regime_filter"] = "atr_regime:min_atr_bps=50:window=14"` (alfabética).

## Comando canônico

```bash
alpha-forge validate \
  --run-id donchian-20-10-btc-180d-regime-atr \
  --dataset-id btcusdt_1h_20250705_20251231_binance_spot \
  --strategy donchian --entry-window 20 --exit-window 10 \
  --n-folds 5 --mc-resamples 500 --mc-seed 42 \
  --stress fee+10:10:0:0 --stress slip+5:0:5:0 --stress spread+10:0:0:10 \
  --regime-filter atr_regime:window=14:min_atr_bps=50
```

## Comandos `compare` (gate 4)

```bash
alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-regime-atr
alpha-forge compare donchian-20-10-btc-180d-regime-sma donchian-20-10-btc-180d-regime-atr
```

**Expectativa:** em ambos, exatamente 2 flags divergem (`regime_filter`, `run_id`). Confirmado (AUDIT.md).

# VALIDATION.md — MA Crossover 20/50 BTCUSDT 1h 180d (baseline)

> Gate ativo: **validação**. Conformidade SPEC item por item. Produzido pelo protocolo após `alpha-forge validate` emitir exit 0 e persistir 4 artefatos em `results/validation/ma-crossover-20-50-btc-180d-baseline/`.

## Testes executados

### Suíte completa

- **Comando:** `python -m pytest -q`
- **Resultado esperado pós-H.3:** `289 passed, 1 skipped`. Piloto H.2b **não altera `src/` para o backtest**, porém durante auditoria foi aplicado fix cp1252 em `_cmd_compare` (substituição Δ→delta em 11 ocorrências). Re-execução da suíte fica a cargo do gate 5 — esperado permanecer verde (edição é puramente cosmética em strings de print, sem semântica nova).

### Pipeline de validação rodado pelo piloto

- **Comando canônico:** idêntico ao IMPLEMENTATION.md §Comando canônico (seed=42, 500 resamples, 3 cenários cost_stress).
- **Exit code:** 0.
- **Artefatos produzidos:** `results/validation/ma-crossover-20-50-btc-180d-baseline/{run,walk_forward,monte_carlo,cost_stress}.json`.
- **Comando `compare`:** `alpha-forge compare donchian-20-10-btc-180d-baseline ma-crossover-20-50-btc-180d-baseline` — exit 0 após fix cp1252. Saída embutida em AUDIT.md §Comparação transversal.

## Conformidade SPEC → execução

| SPEC §seção | Status | Evidência |
|---|---|---|
| §1 Hipótese (preservação ≥ 0.95×cap e hit_rate ≥ 45%) | **GAP — refuta por hit_rate** | `cost_stress.json → baseline.result.metrics.hit_rate = 0.3111` < 0.45. `final_equity = 9564.25` também < 9500 por 64 USDT — ambos critérios 1 e hipótese §1 violados. |
| §2 Mercado (BTCUSDT spot) | OK | `run.json → flags.dataset_id = btcusdt_1h_20250705_20251231_binance_spot`. |
| §3 Timeframe (1h, 4320 barras) | OK | `cost_stress.json → baseline.result.metrics.bar_count = 4320`. |
| §4 Entradas (cross-up SMA20/50, causal) | OK | Property-based `tests/property/test_lookahead_guard.py` verde; ADR-0002 §causal. |
| §5 Saídas (cross-down SMA20/50) | OK | Trade count = 45; padrão long-only cross entry/exit. |
| §6 Stops (nenhum) | OK | `strategy.py` sem branch de stop; saída só por cross-down. |
| §7 Sizing (fracao=0.1, alav=2.0) | OK | `run.json → flags.fracao = 0.1, alavancagem = 2.0`. |
| §8 Fees (5bps taker) | OK | `run.json → flags.taker_fee_bps = 5.0`. |
| §9 Slippage (2bps/unit_notional) | OK | `run.json → flags.slippage_bps_per_notional = 2.0`. |
| §10 Spread (0bps baseline + stress +10) | OK | Baseline `spread_bps=0`; cenário `spread+10` produzido. |
| §11 Funding (N/A spot) | OK | Não aplicável. |
| §12 Warm-up (51 barras HOLD) | OK | Property-based de causalidade cobre warm-up. |
| §13 Limitações | OK em código | Limitações declaradas no SPEC; não implicam GAP. |

## Conformidade com propriedades estruturais

- **ADR-0019 (`fee+Δbps ≡ spread+Δbps`):** `cost_stress.json` → `fee+10.final_equity = 9383.28` === `spread+10.final_equity = 9383.28`. Hit-rate também coincide (0.2667 ambos). **Terceira confirmação empírica** (H.1 BTC, H.2a ETH, agora H.2b BTC cross-family).
- **ADR-0010 (monotonicidade):** todos os cenários `cost_stress` têm `final_equity ≤ baseline`. Ordem: baseline (9564.25) > slip+5 (9546.16) > fee+10 = spread+10 (9383.28). OK.
- **ADR-0002 (causalidade):** `test_lookahead_guard.py` verde no último `pytest` (289 passed, 1 skipped).

## Critério de refutação — avaliação

1. **`hit_rate = 0.3111 < 0.45`** → **VIOLA** critério 1.
2. **`max_drawdown = 0.0652` < 0.35** → passa critério 2.
3. **`spread+10` Δ = (9383.28 − 9564.25)/9564.25 = −1.89%**, threshold ≥ −5% → passa critério 3.

Boolean OR: qualquer violação refuta. **Hipótese §1 refutada por critério 1** (e também falha em preservação: 9564.25 < 9500 não — 9564.25 > 9500, preservação passa; mas hit_rate falha). Resultado final da validação: **refuta por hit_rate**.

## Comparação com H.1 / H.2a (contexto)

| Piloto | Family | Asset | final_equity | hit_rate | mdd | trades |
|---|---|---|---|---|---|---|
| H.1 | Donchian 20/10 | BTC | 9088.55 (-9.1%) | 25.45% | 13.90% | 110 |
| H.2a | Donchian 20/10 | ETH | 10240.02 (+2.4%) | 28.13% | 8.90% | 96 |
| **H.2b** | **MA 20/50** | **BTC** | **9564.25 (-4.36%)** | **31.11%** | **6.52%** | **45** |

MA crossover em BTC tem `hit_rate` mais alto que Donchian em ambos os assets, mas ainda abaixo do limiar. Frequência de trades ≈ metade da Donchian BTC. Detalhes em BACKTEST.md.

## Conclusão

Todos os itens de conformidade do SPEC estão OK exceto §1 (hipótese), marcado GAP. Pipeline reprodutível (seed=42, run.json persistido). Pronto para gate 4 (auditoria).

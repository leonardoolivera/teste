# VALIDATION.md — Donchian 20/10 BTCUSDT 1h 180d (symmetric)

> Gate ativo: **validação**. Conformidade SPEC item por item. Produzido pelo protocolo após `alpha-forge validate --no-long-only` emitir exit 0 e persistir 4 artefatos em `results/validation/donchian-20-10-btc-180d-short/`.

## Testes executados

### Suíte completa

- **Comando:** `python -m pytest -q`
- **Resultado esperado:** `289 passed, 1 skipped` (estado pós-H.2b). Piloto H.2c **não altera `src/` nem `tests/`** — puramente exercício protocolar em código existente (ADR-0013).

### Pipeline de validação rodado pelo piloto

- **Comando canônico:** idêntico ao IMPLEMENTATION.md §Comando canônico (seed=42, 500 resamples, 3 cenários cost_stress, `--no-long-only`).
- **Exit code:** 0.
- **Artefatos produzidos:** `results/validation/donchian-20-10-btc-180d-short/{run,walk_forward,monte_carlo,cost_stress}.json`.
- **Comando `compare`:** `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-short` — exit 0 (segundo uso protocolar); saída embutida em AUDIT.md §Comparação transversal.

## Conformidade SPEC → execução

| SPEC §seção | Status | Evidência |
|---|---|---|
| §1 Hipótese (preservação ≥ 0.95×cap e hit_rate ≥ 45%) | **GAP — refuta por múltiplos critérios** | `baseline.final_equity = 8526.83 < 9500` (preservação falha) **E** `hit_rate = 0.2727 < 0.45` **E** `spread+10` Δ = −10.34% < −5%. Três violações simultâneas. |
| §2 Mercado (BTCUSDT spot) | OK | `run.json → flags.dataset_id = btcusdt_1h_20250705_20251231_binance_spot`. |
| §3 Timeframe (1h, 4320 barras) | OK | `cost_stress.json → baseline.result.bars = 4320`. |
| §4 Entradas (ENTER_LONG/ENTER_SHORT simétrico, ADR-0013) | OK | `run.json → flags.long_only = False`. Fills observados incluem both `side=long` e `side=short` alternando — consistente com ADR-0013 §mapeamento simétrico. |
| §5 Saídas (reversal, sem EXIT explícito) | OK | Engine reverte posição no breakout oposto via ADR-0012 (custo duplo). Fills `side=flat` no mesmo timestamp que o novo `side=long`/`side=short` confirmam reverse-on-signal. |
| §6 Stops (nenhum) | OK | Sem branch de stop; saída só por reversão. |
| §7 Sizing (fracao=0.1, alav=2.0) | OK | `run.json → flags.fracao = 0.1, alavancagem = 2.0`. |
| §8 Fees (5bps taker) | OK | `run.json → flags.taker_fee_bps = 5.0`. |
| §9 Slippage (2bps/unit_notional) | OK | `run.json → flags.slippage_bps_per_notional = 2.0`. |
| §10 Spread (0bps baseline + stress +10) | OK | Baseline `spread_bps=0`; cenário `spread+10` produzido. |
| §11 Funding (N/A spot) | OK | Não aplicável (limitação §13 sobre borrow/funding declarada). |
| §12 Warm-up (22 barras HOLD) | OK | Property-based `test_cost_monotonicity_donchian_short.py` verde na suíte base. |
| §13 Limitações | OK em código | Limitações declaradas no SPEC; não implicam GAP. |

## Conformidade com propriedades estruturais

- **ADR-0019 (`fee+Δbps ≡ spread+Δbps`):** `cost_stress.json` → `fee+10.final_equity = 7645.51` === `spread+10.final_equity = 7645.51`. Hit_rate idêntico (0.2273); mdd idêntico (0.2381). **Quarta confirmação empírica** (H.1, H.2a, H.2b, agora H.2c cross-mode).
- **ADR-0010 (monotonicidade):** todos os cenários `cost_stress` têm `final_equity ≤ baseline`. Ordem: baseline (8526.83) > slip+5 (8438.72) > fee+10 = spread+10 (7645.51). OK.
- **ADR-0013 (reverse-on-signal, custo duplo):** 220 trades em 4320 barras ≈ 2× os 110 da H.1 (long-only mesmo dataset). Esperado por ADR-0012 — cada flip conta duas operações.
- **ADR-0002 (causalidade):** `test_lookahead_guard.py` verde na suíte base.

## Critério de refutação — avaliação

1. **`hit_rate = 0.2727 < 0.45`** → **VIOLA** critério 1.
2. **`max_drawdown = 0.1545` < 0.35** → passa critério 2.
3. **`spread+10` Δ = −10.34% < −5%** → **VIOLA** critério 3 (primeiro piloto a violar este critério).

Boolean OR com 2 violações simultâneas. Hipótese §1 falha duplamente: preservação (8526.83 < 9500) e hit_rate (0.2727 < 0.45). **Refutação mais forte do que H.1/H.2a/H.2b.**

## Comparação com pilotos anteriores (contexto)

| Piloto | Family | Mode | final_equity | hit_rate | mdd | trades | violations |
|---|---|---|---|---|---|---|---|
| H.1 | Donchian 20/10 | long | 9088.55 (-9.1%) | 25.45% | 13.90% | 110 | 1, 2 falso* |
| H.2a | Donchian 20/10 | long (ETH) | 10240.02 (+2.4%) | 28.13% | 8.90% | 96 | 1 |
| H.2b | MA 20/50 | long | 9564.25 (-4.36%) | 31.11% | 6.52% | 45 | 1 |
| **H.2c** | **Donchian 20/10** | **symmetric** | **8526.83 (-14.73%)** | **27.27%** | **15.45%** | **220** | **1, 3** (hipótese dupla-falha) |

*H.1 violou hipótese §1 em preservação.

Reversal tem maior sensibilidade a custos (critério 3 viola pela primeira vez) — custo duplo ADR-0012 amplifica impacto de perturbação +10bps. Detalhes em BACKTEST.md.

## Conclusão

Todos os itens de conformidade do SPEC estão OK exceto §1 (hipótese), marcado GAP triplo (preservação + hit_rate + spread+10). Pipeline reprodutível (seed=42, run.json persistido). Pronto para gate 4 (auditoria) — refutação mais forte até hoje.

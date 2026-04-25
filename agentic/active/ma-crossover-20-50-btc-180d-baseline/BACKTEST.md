# BACKTEST.md — MA Crossover 20/50 BTCUSDT 1h 180d (baseline)

> Gate ativo: **validação**. Métricas + sensibilidade + walk-forward + Monte Carlo. Fonte: `results/validation/ma-crossover-20-50-btc-180d-baseline/*.json`. Timestamp `run.json` = 2026-04-18T01:04:24Z.

## Dataset

- `dataset_id = btcusdt_1h_20250705_20251231_binance_spot`
- 4320 barras 1h (2025-07-05 00:00 UTC → 2025-12-31 23:00 UTC).
- `declared_gaps: []`.
- Mesmo dataset de H.1 por design (único eixo = family/parâmetros).

## Métricas do baseline (full 4320 bars)

- `final_equity = 9564.25` USDT (−4.36% vs 10000 inicial).
- `total_pnl = −435.75` USDT.
- `hit_rate = 31.11%` (14 ganhos / 45 trades).
- `trade_count = 45`.
- `max_drawdown = 6.52%`.

**Observação:** frequência de trades ≈ 41% da Donchian BTC (45 vs 110) — MA crossover é mais conservador (só sinaliza em inversões confirmadas pelas SMAs, não em rompimentos pontuais).

## Sensibilidade a custos (ADR-0014 + ADR-0019)

Cenários de cost_stress aplicados sobre o baseline completo:

| cenário | flags | final_equity | hit_rate | mdd | Δ vs baseline |
|---|---|---|---|---|---|
| baseline | fee=5, slip=2, spread=0 | **9564.25** | 0.3111 | 0.0652 | — |
| fee+10 | fee=15, slip=2, spread=0 | 9383.28 | 0.2667 | 0.0823 | **−180.97 (−1.89%)** |
| slip+5 | fee=5, slip=7, spread=0 | 9546.16 | 0.2889 | 0.0669 | −18.08 (−0.19%) |
| spread+10 | fee=5, slip=2, spread=10 | **9383.28** | 0.2667 | 0.0823 | **−180.97 (−1.89%)** |

**Propriedade estrutural ADR-0019 confirmada terceira vez:**
`fee+10` e `spread+10` produzem `final_equity` **idêntico** (9383.28), `hit_rate` idêntico (0.2667) e `mdd` idêntico (0.0823). Δ PnL = −180.97 em ambos. Isso vale porque `notional/capital_inicial` é constante (fracao × alavancagem = 0.2) — propriedade empírica forte, agora replicada cross-family.

**Monotonicidade (ADR-0010):** `baseline ≥ slip+5 ≥ fee+10 = spread+10`. OK.

## Walk-forward (rolling, 4 folds)

`scheme=rolling`, `train_fraction=0.5`, `min_test_bars=50`. `n_folds` solicitado=5; efetivo=4 (último fold não passa `min_test_bars`).

| fold | train | test | test_bars | trades | pnl | hit_rate |
|---|---|---|---|---|---|---|
| 1 | 2025-07-05 → 2025-08-29 | 2025-08-29 → 2025-10-23 | 1346 | 10 | **−202.91** | 0.3000 |
| 2 | 2025-08-07 → 2025-10-02 | 2025-10-02 → 2025-11-27 | 1346 | 5 | **+120.62** | 0.2000 |
| 3 | 2025-09-09 → 2025-11-04 | 2025-11-04 → 2025-12-30 | 1346 | 5 | **−27.93** | 0.2000 |
| 4 | 2025-10-11 → 2025-12-06 | 2025-12-06 → 2025-12-31 | 628 | 9 | **−305.28** | 0.1111 |
| — | — | **total** | — | **29** | **−415.50** | — |

- **3 de 4 folds negativos**; único fold positivo (fold 2) tem hit_rate = 20% (abaixo do limiar e com N baixo).
- **Delta baseline vs walk-forward: 45 − 29 = 16 trades** ocorrem fora do regime test-only (warm-up das folds pré-split e sobreposição de períodos excluídos).
- Hit rate **não** degrada monotonicamente como em H.2a — padrão mais ruidoso compatível com N baixo.

## Monte Carlo (ADR-0007, seed=42, 500 resamples)

- `seed = 42` (determinismo bit-a-bit).
- `resamples = 500` de barras do baseline com reposição.
- `original_final_equity = 9511.25`.

Percentis de `final_equity`:

| p5 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|
| 9090.97 | 9320.49 | **9525.25** | 9720.55 | 10043.59 |

- **p50 = 9525.25 < 10000** — mediana sub-breakeven (consistente com baseline −4.36%).
- **p95 = 10043.59 > 10000** — apenas o topo da distribuição cruza breakeven. Probabilidade empírica de preservação ≈ 5–10% (extrapolação entre p75 e p95).
- Em linha com H.1 e H.2a: distribuição MC deslocada para baixo indica ausência de edge.

## Comparação transversal (H.1 Donchian BTC vs H.2b MA crossover BTC)

| métrica | H.1 Donchian 20/10 | H.2b MA 20/50 | diff |
|---|---|---|---|
| final_equity | 9088.55 | 9564.25 | +475.70 (+5.23%) |
| hit_rate | 25.45% | 31.11% | +5.66 pp |
| max_drawdown | 13.90% | 6.52% | −7.38 pp |
| trade_count | 110 | 45 | −65 (−59%) |
| MC p50 | ~9100 | 9525.25 | +425 |
| Δ fee+10 | −437.73 | −180.97 | +257 (ganho) |
| Δ spread+10 | −437.73 | −180.97 | idêntico a fee+10 em ambos ✓ |
| release_decision | fail | fail (esperado) | — |

**Leitura cross-family:**
- MA crossover reduz drawdown pela metade e melhora hit_rate em 5.66 pp, mas ainda refuta.
- Menor exposição (menos trades) → menor perda absoluta em cenários de stress (Δ fee+10 −180 vs −437).
- Ambas famílias refutam por hit_rate em BTC 180d — sinal de que o **regime** (não a family) é o fator dominante. Hipótese estrutural para próximos pilotos: filtro de regime antes de varredura de famílias.

Comparação programática via `alpha-forge compare donchian-20-10-btc-180d-baseline ma-crossover-20-50-btc-180d-baseline` (ADR-0018) — documentada em AUDIT.md §Comparação transversal.

## Reprodutibilidade

- Comando canônico: IMPLEMENTATION.md §Comando canônico.
- `run.json` persistido com todas as flags (ADR-0015 + ADR-0017).
- Seed=42 + flags fixas garantem re-execução bit-a-bit.
- Dispensa `PYTHONIOENCODING=utf-8` (H.3).

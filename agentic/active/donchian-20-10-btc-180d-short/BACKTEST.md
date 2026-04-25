# BACKTEST.md — Donchian 20/10 BTCUSDT 1h 180d (symmetric)

> Gate ativo: **validação**. Métricas + sensibilidade + walk-forward + Monte Carlo. Fonte: `results/validation/donchian-20-10-btc-180d-short/*.json`. Timestamp `run.json` = 2026-04-18T01:53:16Z.

## Dataset

- `dataset_id = btcusdt_1h_20250705_20251231_binance_spot`
- 4320 barras 1h (2025-07-05 00:00 UTC → 2025-12-31 23:00 UTC).
- `declared_gaps: []`.
- Mesmo dataset de H.1/H.2b por design (único eixo = modo).

## Métricas do baseline (full 4320 bars)

- `final_equity = 8526.83` USDT (−14.73% vs 10000 inicial).
- `total_pnl = −1473.17` USDT.
- `hit_rate = 27.27%` (60 ganhos / 220 trades).
- `trade_count = 220`.
- `max_drawdown = 15.45%`.

**Observação estrutural:** reversal duplica o número de trades vs H.1 (220 vs 110) — consistente com ADR-0012/ADR-0013: cada flip long↔short é 2 operações (close anterior + open novo), e o universo de sinais oposicionais é simétrico. Custo acumulado por 220 trades × 2 (fill+flip) amplifica PnL negativo.

## Sensibilidade a custos (ADR-0014 + ADR-0019)

Cenários de cost_stress aplicados sobre o baseline completo:

| cenário | flags | final_equity | hit_rate | mdd | Δ vs baseline |
|---|---|---|---|---|---|
| baseline | fee=5, slip=2, spread=0 | **8526.83** | 0.2727 | 0.1545 | — |
| fee+10 | fee=15, slip=2, spread=0 | 7645.51 | 0.2273 | 0.2381 | **−881.32 (−10.34%)** |
| slip+5 | fee=5, slip=7, spread=0 | 8438.72 | 0.2682 | 0.1628 | −88.11 (−1.03%) |
| spread+10 | fee=5, slip=2, spread=10 | **7645.51** | 0.2273 | 0.2381 | **−881.32 (−10.34%)** |

**Propriedade estrutural ADR-0019 confirmada 4ª vez:**
`fee+10` e `spread+10` produzem `final_equity` **idêntico** (7645.51), `hit_rate` idêntico (0.2273), `mdd` idêntico (0.2381). Δ PnL = −881.32 em ambos. Replica cross-mode (agora long E short simétricos) — propriedade é structural-in-cost, não específica de long-only.

**Critério 3 (spread+10 Δ < −5%) **viola**:** −10.34% < −5%. Reversal é ~2.3× mais sensível a perturbação +10 bps do que H.1 long-only (que teve Δ = −4.81%). Mecânica: custo duplo por flip amplifica o delta — cada 10 bps extra se aplica a 2× mais operações.

**Monotonicidade (ADR-0010):** `baseline ≥ slip+5 ≥ fee+10 = spread+10`. OK.

## Walk-forward (rolling, 4 folds)

`scheme=rolling`, `train_fraction=0.5`, `min_test_bars=50`. `n_folds` solicitado=5; efetivo=4.

**Nota de janela:** folds começam em 2025-08-10 (ADR-0013 com reversal tem warm-up equivalente de 22 barras + train de 864 barras ≈ 36 dias → primeiro test só em 2025-08). H.1 usou janelas diferentes porque long-only tem dinâmica distinta — comparação fold-a-fold exige cuidado.

| fold | train | test | test_bars | trades | pnl | hit_rate |
|---|---|---|---|---|---|---|
| 1 | 2025-07-23 → 2025-08-09 | 2025-08-10 → 2025-09-14 | 864 | 45 | **−252.74** | 0.2667 |
| 2 | 2025-08-28 → 2025-09-14 | 2025-09-15 → 2025-10-20 | 864 | 41 | **+102.13** | 0.3902 |
| 3 | 2025-10-03 → 2025-10-20 | 2025-10-21 → 2025-11-25 | 864 | 36 | **−83.18** | 0.3611 |
| 4 | 2025-11-08 → 2025-11-25 | 2025-11-26 → 2025-12-31 | 864 | 45 | **−612.75** | 0.1778 |
| — | — | **total** | — | **167** | **−846.54** | — |

- **3 de 4 folds negativos**; único positivo (fold 2) tem `hit_rate = 39.02%` — mais próximo do limiar de 45% do que qualquer fold de H.1/H.2a/H.2b, mas ainda abaixo.
- Fold 4 (dezembro 2025) com `hit_rate = 17.78%` em 45 trades é o pior — consistente com regime de pullback agudo onde reversal é mais tardio.
- **167 trades em walk-forward vs 220 no baseline full** — delta de 53 trades ocorrem fora do regime test-only (warm-up + sobreposições excluídas).

## Monte Carlo (ADR-0007, seed=42, 500 resamples)

- `seed = 42` (determinismo bit-a-bit).
- `resamples = 500` de barras do baseline com reposição.
- `original_final_equity = 9161.31`.

Percentis de `final_equity`:

| p5 | p25 | p50 | p75 | p95 |
|---|---|---|---|---|
| 8349.93 | 8790.04 | **9114.06** | 9453.75 | 9954.15 |

- **p50 = 9114.06 < 10000** — mediana sub-breakeven.
- **p95 = 9954.15 < 10000** — **primeiro piloto em que nem p95 cruza breakeven**. H.1 teve todos os percentis sub-breakeven também (coincidência estrutural de long-only vs symmetric no mesmo dataset).
- Probabilidade empírica de preservação ≈ 0–5% (abaixo de p95).

## Comparação transversal (H.1 Donchian long vs H.2c Donchian symmetric)

| métrica | H.1 Donchian long | H.2c Donchian symmetric | diff |
|---|---|---|---|
| final_equity | 9088.55 | 8526.83 | **−561.72 (−6.18%)** |
| hit_rate | 25.45% | 27.27% | +1.82 pp (levemente melhor) |
| max_drawdown | 13.90% | 15.45% | +1.55 pp |
| trade_count | 110 | 220 | +110 (×2 exatamente) |
| MC p50 | ~9100 | 9114.06 | ≈0 |
| MC p95 | ~9700 | 9954.15 | +254 |
| Δ fee+10 | −437.73 (−4.81%) | −881.32 (−10.34%) | **−2.15× amplificado** |
| Δ spread+10 | −437.73 | −881.32 | **idêntico a fee+10 em ambos** ✓ |
| release_decision | fail | fail (esperado) | — |

**Leitura cross-mode:**
- Reversal **não gera edge** no regime de 2025-07..12 em BTC — final_equity piora 6.18% vs long-only.
- Dobrar trades dobra o custo sem dobrar o ganho expected — hit_rate sobe 1.82 pp mas magnitude de trades perdedores também cresce.
- Sensibilidade a +10 bps é amplificada 2.15×, coerente com 2× operações. Critério 3 viola pela primeira vez no protocolo.
- Distribuição MC desloca-se levemente para cima em p95 (254 USDT) mas mediana idêntica — reversal não muda a forma da distribuição, só adiciona variância.

Comparação programática via `alpha-forge compare donchian-20-10-btc-180d-baseline donchian-20-10-btc-180d-short` (ADR-0018, 2º uso protocolar) — documentada em AUDIT.md §Comparação transversal.

## Reprodutibilidade

- Comando canônico: IMPLEMENTATION.md §Comando canônico.
- `run.json` persistido com `long_only=False` explícito (ADR-0015 + ADR-0017).
- Seed=42 + flags fixas garantem re-execução bit-a-bit.
- Dispensa `PYTHONIOENCODING=utf-8` (H.3 + fix de H.2b em `_cmd_compare`).

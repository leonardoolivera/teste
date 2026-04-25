# BACKTEST.md — Donchian 20/10 + Composite(sma AND atr) (H.5)

## Dataset

- `btcusdt_1h_20250705_20251231_binance_spot` — BTCUSDT 1h, 2025-07-05 00:00 UTC a 2025-12-31 23:00 UTC, 4320 barras, `declared_gaps: []`.
- Idêntico a H.1 / H.3 / H.4 — permite experimento controlado triplo.

## Métricas

### Baseline (cost_stress scenario_index=0)

| métrica          | valor       |
| ---------------- | ----------- |
| final_equity     | 9247.34     |
| hit_rate         | 29.73%      |
| total_trades     | 74          |
| max_drawdown     | 8.14%       |

### Stress scenarios

| scenario  | final_equity | hit_rate | trades | mdd    | Δ fe vs baseline |
| --------- | ------------ | -------- | ------ | ------ | ---------------- |
| baseline  | 9247.34      | 29.73%   | 74     | 8.14%  | —                |
| fee+10    | 8953.15      | 20.27%   | 74     | 10.99% | −3.18%           |
| slip+5    | 9217.96      | 28.38%   | 74     | 8.42%  | −0.32%           |
| spread+10 | 8953.15      | 20.27%   | 74     | 10.99% | −3.18%           |

Δ `spread+10` / baseline = **0.9682** (acima do piso 0.95 — **critério 3 passa**).

### Walk-forward (5-fold rolling, train_fraction=0.5)

| fold | fe      | hit_rate | trades | mdd   |
| ---- | ------- | -------- | ------ | ----- |
| 0    | 9884.54 | 9.09%    | 11     | 1.30% |
| 1    | 9975.85 | 46.67%   | 15     | 0.66% |
| 2    | 9687.32 | 25.00%   | 16     | 3.50% |
| 3    | 9868.60 | 38.46%   | 13     | 3.01% |

Soma de trades dos folds (11+15+16+13=55) < cost_stress baseline (74) — esperado, folds cobrem subset do histórico.

### Monte Carlo bootstrap (500 resamples, seed=42)

| p | final_equity | mdd   |
| - | ------------ | ----- |
| 5 | 9076.24      | 3.30% |
| 50| 9402.51      | 6.50% |
| 95| 9808.96      | 9.45% |

## Compare triplo (flags diff e deltas numéricos)

### H.1 ↔ H.5 (baseline vs composto)

- flags diff: `regime_filter` (`none` → `and(atr...,sma...)`), `run_id`.
- `total_trades`: 110 → 74 (Δ=−36, −32.7%).
- `baseline final_equity`: 9089.79 → 9247.34 (Δ=+157.55).
- `baseline hit_rate`: 25.45% → 29.73% (Δ=+4.28 p.p.).
- `baseline mdd`: 10.49% → 8.14% (Δ=−2.35 p.p.).

### H.3 ↔ H.5 (sma-only vs composto)

- flags diff: `regime_filter` (`sma_slope:...` → `and(atr...,sma...)`), `run_id`.
- `total_trades`: 114 → 74 (Δ=−40).
- `baseline final_equity`: 9195.59 → 9247.34 (Δ=+51.75).
- `baseline hit_rate`: 29.82% → 29.73% (Δ=−0.09 p.p.) — **praticamente inalterado**.
- `baseline mdd`: 9.60% → 8.14% (Δ=−1.46 p.p.).

### H.4 ↔ H.5 (atr-only vs composto)

- flags diff: `regime_filter` (`atr_regime:...` → `and(atr...,sma...)`), `run_id`.
- `total_trades`: 72 → **74** (Δ=**+2**) ⚠️ **direção contra-intuitiva**.
- `baseline final_equity`: 9180.45 → 9247.34 (Δ=+66.89).
- `baseline hit_rate`: 26.39% → 29.73% (Δ=+3.34 p.p.).
- `baseline mdd`: 8.80% → 8.14% (Δ=−0.66 p.p.).
- Sobre WF fold-sum trades: H.4=60 vs H.5=55 (Δ=−5) — **no nível fold-agregado, AND É mais restritivo**. A inversão só aparece sobre o período inteiro (cost_stress baseline).

## Quadro comparativo consolidado (H.1, H.3, H.4, H.5)

| piloto | regime_filter       | fe     | hit_rate | trades | mdd   |
| ------ | ------------------- | ------ | -------- | ------ | ----- |
| H.1    | none                | 9089.79| 25.45%   | 110    | 10.49%|
| H.3    | sma_slope           | 9195.59| 29.82%   | 114    | 9.60% |
| H.4    | atr_regime          | 9180.45| 26.39%   | 72     | 8.80% |
| **H.5**| **and(atr, sma)**   |**9247.34**|**29.73%**|**74**|**8.14%**|

- H.5 tem o **melhor final_equity**, **melhor max_drawdown** e o **segundo melhor hit_rate** — mas nenhum cruza os pisos do critério de refutação.
- Trade_count: H.3 (114) > H.1 (110) > H.5 (74) > H.4 (72). **AND (74) não é estritamente menor que min(H.3=114, H.4=72)**: violação da leitura ingênua de ADR-0023 property 1 em nível de trade_count. Ver AUDIT.md.

## Observações

- **Sétima confirmação ADR-0019** (`fee+Δ == spread+Δ` em final_equity).
- **Melhor p5 Monte Carlo do protocolo H**: 9076.24 (0.908×capital).
- **Segundo fold a cruzar 45%** no protocolo (H.3 fold 2 foi o primeiro; H.5 fold 1 agora).
- **Finding não esperado:** AND aumentou o trade_count relativo a ATR-alone (+2). Causa raiz e lição transversal em AUDIT.md.

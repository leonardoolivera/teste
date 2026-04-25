# BACKTEST.md — H.8 Donchian 40/20 BTC 180d

## Dataset

`btcusdt_1h_20250705_20251231_binance_spot` — 4320 barras.

## Métricas

### Baseline

| métrica      | valor   |
| ------------ | ------- |
| final_equity | 9528.27 |
| hit_rate     | 24.49%  |
| total_trades | 49      |
| max_drawdown | 6.51%   |

### Stress

| scenario  | fe      | hit    | mdd   | Δ fe    |
| --------- | ------- | ------ | ----- | ------- |
| baseline  | 9528.27 | 24.49% | 6.51% | —       |
| fee+10    | 9333.41 | 24.49% | 8.33% | −2.04%  |
| slip+5    | 9508.81 | 24.49% | 6.70% | −0.21%  |
| spread+10 | 9333.41 | 24.49% | 8.33% | −2.04%  |

Δ spread+10 / baseline = 0.9796 — **melhor robustez a custos do protocolo**.

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 0    | 9894.71  | 25.00% | 8      |
| 1    | 10127.04 | 28.57% | 7      |
| 2    | 9970.06  | 33.33% | 6      |
| 3    | 9683.28  | 8.33%  | 12     |

Fold 1 **fe > 10000** (segunda vez no protocolo BTC — primeira foi H.7 fold 1).

### MC (500, seed=42)

p5=9301.29 | p50=9606.00 | p95=9948.72

## Observações

- **Trade_count 49 — segundo menor do protocolo** (depois só H.4 72 — espera, H.8=49 é MENOR).
- Corrigindo: H.8 com 49 trades é **o menor trade_count absoluto** do protocolo (H.4 tinha 72).
- Hit degrada vs H.1 (25.45→24.49%) — mas custos são quase neutros.
- Fold 3 hit=8.33% — fold extremamente ruim, 12 trades.

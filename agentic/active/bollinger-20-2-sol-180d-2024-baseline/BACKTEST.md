# BACKTEST.md — J.1 Bollinger 20/2 SOL 180d 2024

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — SOLUSDT 1h, 4320 barras, sha256=`4cdcf8ce`.
Janela 2024-07-05 → 2024-12-31 (não-correlata com I.1).

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | **10684.24** |
| hit_rate     | **67.82%** |
| total_trades | 87       |
| max_drawdown | **3.43%** |

### Stress

| scenario  | fe       | hit    | mdd   | Δ fe   |
| --------- | -------- | ------ | ----- | ------ |
| baseline  | 10684.24 | 67.82% | 3.43% | —      |
| fee+10    | 10335.23 | 64.37% | 3.60% | −3.27% |
| slip+5    | 10649.23 | 67.82% | 3.45% | −0.33% |
| spread+10 | 10335.23 | 64.37% | 3.60% | −3.27% |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 1    | 10150.53 | 72.22% | 18     |
| 2    | 9931.39  | 47.06% | 17     |
| 3    | 10318.32 | **88.24%** | 17   |
| 4    | 10144.55 | 65.00% | 20     |

**4/4 folds cruzam 45%.** Fold 3 atinge 88.24% — maior hit por fold do protocolo inteiro.

### MC (500, seed=42)

p5=**10046.92** (acima do capital!) | p50=10666.56 | p95=11182.65

## Cross-window SOL (I.1 2025 vs J.1 2024)

| janela      | fe       | hit    | trades | mdd   | MC p5    |
| ----------- | -------- | ------ | ------ | ----- | -------- |
| I.1 2025-H2 | 10189.15 | 65.85% | 82     | 6.93% | 9277.98  |
| **J.1 2024-H2** | **10684.24** | **67.82%** | **87** | **3.43%** | **10046.92** |

**J.1 domina I.1 em todos os eixos.** Edge mean-reversion é **mais forte em 2024-H2** que em 2025-H2 para SOL.

# BACKTEST.md — J.3 Bollinger 20/2 ETH 180d 2024

## Dataset

`ethusdt_1h_20240705_20241231_binance_spot` — ETHUSDT 1h, 4320 barras, sha256=`75914a9b`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9977.19 (−0.23%) |
| hit_rate     | **71.76%** (maior do protocolo) |
| total_trades | 85       |
| max_drawdown | 5.93%    |

### Stress

| scenario  | fe      | hit    | Δ fe   |
| --------- | ------- | ------ | ------ |
| baseline  | 9977.19 | 71.76% | —      |
| fee+10    | 9637.58 | 68.24% | −3.40% |
| slip+5    | 9943.19 | 71.76% | −0.34% |
| spread+10 | 9637.58 | 68.24% | −3.40% |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 1    | 10267.90 | **83.33%** | 18 |
| 2    | 9928.85  | 64.71% | 17     |
| 3    | 10256.82 | 81.25% | 16     |
| 4    | 9816.54  | 62.50% | 16     |

**4/4 folds cruzam 45%.** Fold 1 e 3 têm hit >80%.

### MC (500, seed=42)

p5=9732.77 | p50=10304.87 | p95=10843.37

## Cross-window ETH (I.3 2025 vs J.3 2024)

| janela | fe       | hit    | trades | mdd   |
| ------ | -------- | ------ | ------ | ----- |
| I.3 2025-H2 | 10057.17 | 63.41% | 82 | 5.17% |
| **J.3 2024-H2** | 9977.19 | **71.76%** | 85 | 5.93% |

**Inversão intrigante:** J.3 tem hit +8.35 pp mas fe −0.80% vs I.3. Distribuição de
magnitude dos trades difere — hit alto não implica fe alto quando vencedores são
pequenos ou quando posição sizing × volatilidade muda entre janelas.

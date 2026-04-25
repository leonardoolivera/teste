# BACKTEST.md — K.1 Bollinger 20/1.5 SOL 180d 2024

## Dataset

`solusdt_1h_20240705_20241231_binance_spot` — 4320 barras.

## Métricas

### Baseline

| métrica      | valor     |
| ------------ | --------- |
| final_equity | **10872.74** (maior fe do protocolo) |
| hit_rate     | 64.96%    |
| total_trades | 117 (+34% vs J.1) |
| max_drawdown | 4.01%     |

### Stress

| scenario  | fe       | hit    | Δ fe   |
| --------- | -------- | ------ | ------ |
| baseline  | 10872.74 | 64.96% | —      |
| fee+10    | 10403.48 | 60.68% | −4.32% |
| slip+5    | 10827.11 | 64.96% | −0.42% |
| spread+10 | 10403.48 | 60.68% | −4.32% |

### WF (4 folds)

| fold | hit    |
| ---- | ------ |
| 1    | 68.18% |
| 2    | 57.14% |
| 3    | **85.19%** |
| 4    | 46.15% |

### MC (500, seed=42)

p5=9960.60 | p50=10681.61 | p95=11387.13

## Comparação K.1 (1.5) vs J.1 (2.0)

| métrica | K.1 | J.1 | Δ |
|---------|-----|-----|---|
| hit | 64.96% | 67.82% | −2.86 pp |
| fe | 10872.74 | 10684.24 | +1.77% |
| trades | 117 | 87 | +34% |

Banda mais estreita gera mais sinais, hit ligeiramente menor, mas fe agregado maior —
volume compensa precisão. Trade-off esperado.

# BACKTEST.md — H.7 Donchian 10/5 BTC 180d

## Dataset

`btcusdt_1h_20250705_20251231_binance_spot` — BTCUSDT 1h, 4320 barras. Idêntico a H.1-H.6.

## Métricas

### Baseline

| métrica      | valor   |
| ------------ | ------- |
| final_equity | 9532.45 |
| hit_rate     | 31.77%  |
| total_trades | 192     |
| max_drawdown | 5.94%   |

### Stress

| scenario  | fe      | hit    | mdd    | Δ fe    |
| --------- | ------- | ------ | ------ | ------- |
| baseline  | 9532.45 | 31.77% | 5.94%  | —       |
| fee+10    | 8766.17 | 23.96% | 13.14% | −8.04%  |
| slip+5    | 9455.78 | 31.77% | 6.65%  | −0.80%  |
| spread+10 | 8766.17 | 23.96% | 13.14% | −8.04%  |

### WF (4 folds)

| fold | fe      | hit    | trades |
| ---- | ------- | ------ | ------ |
| 0    | 9862.64 | 30.77% | 39     |
| 1    | 9981.87 | 39.47% | 38     |
| 2    | 9804.72 | 24.32% | 37     |
| 3    | 9910.08 | 26.32% | 38     |

### MC (500, seed=42)

p5=9122.21 | p50=9585.33 | **p95=10116.28** (primeiro p95 > 10000 com Donchian BTC!)

## Observações

- **Trade_count 192** — maior do protocolo. Janela menor capta mais rompimentos.
- **p95 MC cruza 10000** — sinal de cauda superior positiva, mas p5 e p50 continuam sub-breakeven.
- **Critério 3 quebra** — janela menor = mais trades = custos dominam em stress.
- Nenhum fold cruza 45% (fold 1 = 39.47%, melhor).

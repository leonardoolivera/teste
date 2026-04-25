# BACKTEST.md — H.10 Donchian 20/10 SOL 180d

## Dataset

`solusdt_1h_20250705_20251231_binance_spot` — SOLUSDT 1h, 4320 barras, `declared_gaps: []`.

## Métricas

### Baseline

| métrica      | valor   |
| ------------ | ------- |
| final_equity | 9119.73 |
| hit_rate     | 31.07%  |
| total_trades | 103     |
| max_drawdown | 14.55%  |

### Stress

| scenario  | fe      | hit    | mdd    | Δ fe    |
| --------- | ------- | ------ | ------ | ------- |
| baseline  | 9119.73 | 31.07% | 14.55% | —       |
| fee+10    | 8709.91 | 29.13% | 16.90% | −4.49%  |
| slip+5    | 9078.77 | 30.10% | 14.78% | −0.45%  |
| spread+10 | 8709.91 | 29.13% | 16.90% | −4.49%  |

### WF (4 folds)

| fold | fe       | hit      | trades |
| ---- | -------- | -------- | ------ |
| 0    | 10244.73 | **47.62%**| 21     |
| 1    | 9734.39  | 30.00%   | 20     |
| 2    | 9716.47  | 26.32%   | 19     |
| 3    | 9300.02  | 9.52%    | 21     |

**Fold 0 cruza 45% — corroboração passa.** Fold 3 hit=9.52% (pior fold isolado do protocolo depois de H.4 fold 0 = 9.09%). Fold 0 fe > 10000.

### MC (500, seed=42)

p5=8038.61 (menor p5 do protocolo) | p50=8952.82 | p95=9915.97

## Observações

- **Distribuição fold-a-fold é a mais polarizada do protocolo** (hit 47.62% → 9.52%; σ~16 pp). Coerente com SOL ser mais volátil que BTC/ETH.
- **Max_drawdown = 14.55% — maior do protocolo** (H.1 10.49%, H.7 5.94%, H.9 6.64%).
- **MC p5 = 8038.61** — menor cauda inferior do protocolo; capital pode cair 20% em cenário desfavorável. Ainda assim, critério 2 passa (14.55% < 35%).

## Quadro cross-asset consolidado (baseline sem filtro, Donchian 20/10 long-only)

| piloto | asset | fe      | hit    | trades | mdd    |
| ------ | ----- | ------- | ------ | ------ | ------ |
| H.1    | BTC   | 9089.79 | 25.45% | 110    | 10.49% |
| H.2a   | ETH   | 10239.86| 28.13% | 107    | ?      |
| **H.10**| **SOL** | **9119.73** | **31.07%** | **103** | **14.55%** |

- SOL hit=31.07% é o maior de baseline-sem-filtro; BTC é o menor (25.45%).
- ETH tem o melhor fe, SOL o pior mdd.
- Tradeoffs claros: volatilidade↑ = hit↑ + mdd↑.

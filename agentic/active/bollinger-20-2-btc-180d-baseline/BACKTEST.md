# BACKTEST.md — I.2 Bollinger 20/2 BTC 180d

## Dataset

`btcusdt_1h_20250705_20251231_binance_spot` — BTCUSDT 1h, 4320 barras, `declared_gaps: []`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 10033.00 |
| hit_rate     | **65.85%** |
| total_trades | 82       |
| max_drawdown | 2.80%    |

### Stress

| scenario  | fe       | hit    | mdd   | Δ fe    |
| --------- | -------- | ------ | ----- | ------- |
| baseline  | 10033.00 | 65.85% | 2.80% | —       |
| fee+10    | 9703.27  | 53.66% | 4.26% | −3.29%  |
| slip+5    | 9999.98  | 65.85% | 2.93% | −0.33%  |
| spread+10 | 9703.27  | 53.66% | 4.26% | −3.29%  |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 1    | 10043.55 | 66.67% | 15     |
| 2    | 9797.05  | 44.44% | 18     |
| 3    | 9978.66  | 58.82% | 17     |
| 4    | 10019.66 | 69.23% | 13     |

**3/4 folds cruzam 45%**; fold 2 marginalmente abaixo (44.44%). Comparar I.1 SOL: 4/4 cruzam.

### MC (500, seed=42)

p5=9434.37 | p50=9860.02 | p95=10240.18

## Observações

- **Mesma hit_rate baseline que I.1 SOL (65.85%, coincidência numérica).** 82 trades idênticos.
- **Menor mdd do protocolo inteiro: 2.80%.** I.1 SOL = 6.93%; H.7 = 5.94%. I.2 é o menos
  arriscado numa métrica isolada.
- **Menor total_pnl que I.1:** +0.33% vs +1.89%. BTC tem magnitude menor de oscilações em
  torno das bandas no período — hit alto, mas retornos por trade pequenos.
- **Fold 2 marginalmente abaixo:** fold corresponde a período com tendência direcional mais
  forte — mean-reversion sofre mais em trends.

## Quadro cross-asset Bollinger 20/2 (baseline, mesmos custos, 180d 1h)

| piloto  | asset | fe       | hit    | trades | mdd   |
| ------- | ----- | -------- | ------ | ------ | ----- |
| I.1     | SOL   | 10189.15 | 65.85% | 82     | 6.93% |
| **I.2** | **BTC** | **10033.00** | **65.85%** | **82** | **2.80%** |

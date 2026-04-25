# BACKTEST.md — H.9 Donchian 20/10 ETH 180d + SMA

## Dataset

`ethusdt_1h_20250705_20251231_binance_spot` — ETHUSDT 1h, 4320 barras, `declared_gaps: []`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | **10504.18** |
| hit_rate     | 32.29%   |
| total_trades | 96       |
| max_drawdown | 6.64%    |

### Stress

| scenario  | fe       | hit    | mdd   | Δ fe    |
| --------- | -------- | ------ | ----- | ------- |
| baseline  | 10504.18 | 32.29% | 6.64% | —       |
| fee+10    | 10119.56 | 31.25% | 8.36% | −3.66%  |
| slip+5    | 10465.59 | 32.29% | 6.80% | −0.37%  |
| spread+10 | 10119.56 | 31.25% | 8.36% | −3.66%  |

### WF (4 folds)

| fold | fe       | hit    | trades |
| ---- | -------- | ------ | ------ |
| 0    | 9960.10  | 28.57% | 14     |
| 1    | 10069.21 | 38.10% | 21     |
| 2    | 9808.16  | 25.00% | 16     |
| 3    | 9895.36  | 22.22% | 18     |

Fold 1 fe > 10000.

### MC (500, seed=42)

p5=9029.01 | p50=9754.50 | **p95=10444.53**

## Cross-asset comparação H.3 (BTC+SMA) ↔ H.9 (ETH+SMA)

- flags diff: `dataset_id`, `run_id` — **exatamente 2**.
- fe: 9195.59 → **10504.18** (Δ=+1308.59, +14.23%).
- hit: 29.82% → 32.29% (Δ=+2.47 pp).
- trades: 114 → 96 (Δ=−18).
- mdd: 9.60% → 6.64% (Δ=−2.96 pp).

**ETH Pareto-domina BTC em todas as métricas** com mesmo filtro/estratégia. Confirma que asset é dimensão crítica — BTC 180d tem menos edge residual que ETH 180d no período.

## Observações

- Primeiro piloto do protocolo com `final_equity > 10000`. **Corroboração passa pela primeira vez em termo absoluto.**
- Hit_rate é o maior de qualquer piloto com filtro (32.29 vs H.5 29.73).
- ADR-0019 confirmada na 11ª execução, primeira vez com fe > 10000.

# BACKTEST.md — M.3 Bollinger 20/2 ETH 4h 2024

## Dataset

`ethusdt_4h_20240705_20241231_binance_spot` — 1080 barras 4h, sha256=`960919b7`.

## Métricas

### Baseline

| métrica      | valor    |
| ------------ | -------- |
| final_equity | 9327.15  |
| hit_rate     | **43.75%** |
| total_trades | 16       |
| max_drawdown | 8.54%    |

**Único piloto da Série M com critério 1 violado (hit < 45%).** Também o pior fe do trio.

### Stress

| scenario  | fe      | hit    | Δ fe    | ratio |
| --------- | ------- | ------ | ------- | ----- |
| baseline  | 9327.15 | 43.75% | —       | 1.000 |
| fee+10    | 9264.56 | 37.50% | −0.67%  | 0.9933 |
| slip+5    | 9320.94 | 43.75% | −0.07%  | 0.9993 |
| spread+10 | 9264.56 | 37.50% | −0.67%  | 0.9933 |

### WF (4 folds)

| fold | trades | hit    |
| ---- | ------ | ------ |
| 1    | 4      | 50.00% |
| 2    | 2      | 50.00% |
| 3    | 3      | 66.67% |
| 4    | 3      | 66.67% |

**4/4 folds cruzam 45% (!)** — mas baseline consolidado falha. Paradoxo amostra-pequena:
cada fold teve sorte, agregado não.

### MC (500, seed=42)

p5=9374.48 | p50=9775.43 | p95=10251.12

## Quadro consolidado trio M (4h, 2024-H2)

| asset | hit baseline | fe | mdd | trades | spread+10/base | status |
|-------|--------------|-----|-----|--------|----------------|--------|
| SOL (M.1) | 57.14% | 9766.99 | 6.99% | 21 | 0.9915 | fail (fe<capital) |
| BTC (M.2) | 52.63% | 9932.49 | 4.38% | 19 | 0.9924 | fail (fe<capital) |
| ETH (M.3) | 43.75% | 9327.15 | 8.54% | 16 | 0.9933 | fail (hit<45% + fe<capital) |

**3/3 fail. Trade-off 4h confirmado.**

## Quadro duplo L + M (trade-off timeframe completo, SOL como referência)

| timeframe | trades | hit | fe | spread+10/base | bottleneck |
|-----------|--------|-----|-----|----------------|------------|
| 15m (L.1) | 336    | 63.10% | 10433.99 | **0.871** | custos |
| **1h (J.1)** | **87** | **67.82%** | **10684.24** | **0.967** | **nenhum** |
| 4h (M.1) | 21 | 57.14% | 9766.99 | 0.9915 | amostra |

**1h é o sweet spot formalmente delimitado.**

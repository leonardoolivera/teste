# BACKTEST.md - T.3 Bollinger BTC 1h 2024 + atr_regime:100

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10270.78 |
| total_pnl | +270.78 |
| trade_count | 16 |
| hit_rate | 75.00% |
| max_drawdown | 2.23% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10270.78 | 1.000 |
| fee+10 | 10206.30 | 0.9937 |
| spread+10 | 10206.30 | 0.9937 |

`fee+10 ≡ spread+10 = 10206.30` (ADR-0019 Série T).

## Monte Carlo

p5 = 10147.85.

## Curva BTC+atr_regime

T.3: above BTC q75 (89.3) - near over-filter edge; 16tr marginal but best ratio/MC p5/hit.

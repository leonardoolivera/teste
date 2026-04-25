# BACKTEST.md - Y.1

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 9923.42 |
| total_pnl | -76.58 |
| trade_count | 97 |
| hit_rate | 43.30% |
| max_drawdown | 3.33% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 9923.42 | 1.000 |
| fee+10 | 9533.95 | 0.9608 |
| spread+10 | 9533.95 | 0.9608 |

`fee+10 ≡ spread+10 = 9533.95` (ADR-0019 Série Y).

## Monte Carlo

p5 = 9265.82.

## Série Y - Donchian BTC + atr - cross-strategy filter test

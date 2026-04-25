# BACKTEST.md - T.1 Bollinger BTC 1h 2024 + atr_regime:35

## Dataset

`btcusdt_1h_20240705_20241231_binance_spot` - 4320 barras 1h.

## Métricas Baseline

| Métrica | Valor |
|---|---:|
| final_equity | 10266.05 |
| total_pnl | +266.05 |
| trade_count | 79 |
| hit_rate | 68.35% |
| max_drawdown | 3.62% |

## Cost stress

| Cenário | final_equity | ratio |
|---|---:|---:|
| baseline | 10266.05 | 1.000 |
| fee+10 | 9949.84 | 0.9692 |
| spread+10 | 9949.84 | 0.9692 |

`fee+10 ≡ spread+10 = 9949.84` (ADR-0019 Série T).

## Monte Carlo

p5 = 9914.44.

## Curva BTC+atr_regime

T.1: below q15 BTC ATR (46.5) - filter mostly inactive, few extra signals.

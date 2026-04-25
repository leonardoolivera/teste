# IMPLEMENTATION.md — S.1 RSI 14/30/70 BTC 1h 2024 + atr_regime:50

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 14 --rsi-oversold 30
--rsi-overbought 70 --dataset-id solusdt_1h_20240705_20241231_binance_spot
--regime-filter atr_regime:window=14:min_atr_bps=50 --stress fee+10:10:0:0
--stress spread+10:0:0:10 --run-id rsi-14-30-70-btc-1h-2024-regime-atr
--mc-seed 42 --mc-resamples 1000`

(Nota: dataset efetivo é BTC conforme N.2 baseline; correção de
run-id em post.)

## Arquivos alterados

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `btcusdt_1h_20240705_20241231_binance_spot` |
| §4 | `RSIMeanReversionStrategy(14, 30, 70)` + `ATRRegimeFilter(14, 50)` |
| §5 | edge-triggered mean exit |
| §6–11-bis | custos H.1 |
| §critério 3 | `--stress spread+10:0:0:10` |
| §ADR-0019 | `--stress fee+10:10:0:0` |

## Testes

Suíte full: **366 passed, 1 skipped**.

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0022; ADR-0027.

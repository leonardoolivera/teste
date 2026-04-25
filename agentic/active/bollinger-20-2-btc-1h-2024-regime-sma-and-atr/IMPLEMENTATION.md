# IMPLEMENTATION.md — P.3 Bollinger BTC 1h 2024 + composite AND

> Gate: **implementação**. Zero código novo; reuso de ADR-0023 `CompositeFilter`.

## CLI

`alpha-forge validate --strategy bollinger --bollinger-window 20
--bollinger-num-std 2.0 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
--regime-filter 'and(atr_regime:min_atr_bps=50:window=14,sma_slope:min_slope_bps=10:window=50)'
--stress fee+10:10:0:0 --stress spread+10:0:0:10
--run-id bollinger-20-2-btc-1h-2024-regime-sma-and-atr
--mc-seed 42 --mc-resamples 1000`

## Arquivos alterados (por este piloto)

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `btcusdt_1h_20240705_20241231_binance_spot` |
| §4 | `BollingerMeanReversionStrategy` + `CompositeFilter(mode="and", [ATRRegimeFilter(14,50), SMASlopeFilter(50,10)])` |
| §5 | edge-triggered mean exit |
| §6–11-bis | custos H.1 |
| §critério 3 | `--stress spread+10:0:0:10` |
| §ADR-0019 | `--stress fee+10:10:0:0` |

## Testes

Suíte full: **366 passed, 1 skipped**.

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0022; ADR-0023; ADR-0026.

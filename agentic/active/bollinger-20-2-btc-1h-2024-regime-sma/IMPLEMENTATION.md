# IMPLEMENTATION.md — P.1 Bollinger BTC 1h 2024 + sma_slope

> Gate: **implementação**. Zero código novo; reuso total de ADR-0022 `sma_slope`.

## CLI

`alpha-forge validate --strategy bollinger --bollinger-window 20
--bollinger-num-std 2.0 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
--regime-filter sma_slope:window=50:min_slope_bps=10 --stress fee+10:10:0:0
--stress spread+10:0:0:10 --run-id bollinger-20-2-btc-1h-2024-regime-sma
--mc-seed 42 --mc-resamples 1000`

## Arquivos alterados (por este piloto)

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `btcusdt_1h_20240705_20241231_binance_spot` |
| §4 | `BollingerMeanReversionStrategy(window=20, num_std=2.0, long_only=True)` + `SMASlopeFilter(window=50, min_slope_bps=10)` |
| §5 | edge-triggered mean exit |
| §6–11-bis | custos H.1, budget padrão |
| §critério 3 | `--stress spread+10:0:0:10` |
| §ADR-0019 | `--stress fee+10:10:0:0` para confirmar equivalência bit-a-bit |

## Testes

Suíte full: **366 passed, 1 skipped** (inalterado — zero código novo).

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0022; ADR-0026; ADR-0027.

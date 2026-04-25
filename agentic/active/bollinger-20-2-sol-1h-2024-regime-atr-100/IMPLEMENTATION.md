# IMPLEMENTATION.md — R.1 Bollinger SOL 1h 2024 + atr_regime:100

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy bollinger --bollinger-window 20
--bollinger-num-std 2.0 --dataset-id solusdt_1h_20240705_20241231_binance_spot
--regime-filter atr_regime:window=14:min_atr_bps=100 --stress fee+10:10:0:0
--stress spread+10:0:0:10 --run-id bollinger-20-2-sol-1h-2024-regime-atr-100
--mc-seed 42 --mc-resamples 1000`

## Arquivos alterados (por este piloto)

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `solusdt_1h_20240705_20241231_binance_spot` |
| §4 | `BollingerMeanReversionStrategy(20, 2.0, long_only=True)` + `ATRRegimeFilter(14, 100)` |
| §5 | edge-triggered mean exit |
| §6–11-bis | custos H.1 |
| §critério 3 | `--stress spread+10:0:0:10` |
| §ADR-0019 | `--stress fee+10:10:0:0` |

## Testes

Suíte full: **366 passed, 1 skipped**.

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0022; ADR-0026.

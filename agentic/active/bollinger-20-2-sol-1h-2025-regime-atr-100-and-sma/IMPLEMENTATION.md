# IMPLEMENTATION.md - AC.2

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --dataset-id solusdt_1h_20250705_20251231_binance_spot --regime-filter and(atr_regime:window=14:min_atr_bps=100,sma_slope:window=50:min_slope_bps=10) --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-2-sol-1h-2025-regime-atr-100-and-sma --mc-seed 42 --mc-resamples 1000`

## Arquivos alterados

Nenhum.

## Mapeamento SPEC → execução

| SPEC | Execução |
|---|---|
| dataset | `solusdt_1h_20250705_20251231_binance_spot` |
| strategy | `BollingerMeanReversionStrategy (causal)` |
| filter | `and(atr_regime:window=14:min_atr_bps=100,sma_slope:window=50:min_slope_bps=10)` |

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Invariantes

ADR-0010; ADR-0019; ADR-0022; ADR-0026.

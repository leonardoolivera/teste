# IMPLEMENTATION.md - V.2 bollinger BTC 1h 2024

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy bollinger --bollinger-window 20 --bollinger-num-std 2.0 --dataset-id btcusdt_1h_20240705_20241231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=85 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id bollinger-20-2-btc-1h-2024-regime-atr-85 --mc-seed 42 --mc-resamples 1000`

## Arquivos alterados

Nenhum.

## Mapeamento SPEC → execução

| SPEC | Execução |
|---|---|
| dataset | `btcusdt_1h_20240705_20241231_binance_spot` |
| strategy | `BollingerMeanReversionStrategy(20, 2.0, long_only=True)` |
| filter | `atr_regime:window=14:min_atr_bps=85` |
| custos | H.1 |

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Invariantes

ADR-0010; ADR-0019; ADR-0022; ADR-0026.

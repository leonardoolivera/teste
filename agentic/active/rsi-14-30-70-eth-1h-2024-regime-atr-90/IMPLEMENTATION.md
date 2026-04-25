# IMPLEMENTATION.md - AB.2

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70 --dataset-id ethusdt_1h_20240705_20241231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=90 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id rsi-14-30-70-eth-1h-2024-regime-atr-90 --mc-seed 42 --mc-resamples 1000`

## Arquivos alterados

Nenhum.

## Mapeamento SPEC → execução

| SPEC | Execução |
|---|---|
| dataset | `ethusdt_1h_20240705_20241231_binance_spot` |
| strategy | `RSIMeanReversionStrategy(14, 30, 70)` |
| filter | `atr_regime:window=14:min_atr_bps=90` |

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Invariantes

ADR-0010; ADR-0019; ADR-0022; ADR-0027.

# IMPLEMENTATION.md - Y.1 donchian BTC 1h 2024

> Gate: **implementação**. Zero código novo.

## CLI

`alpha-forge validate --strategy donchian --entry-window 20 --exit-window 10 --dataset-id btcusdt_1h_20240705_20241231_binance_spot --regime-filter atr_regime:window=14:min_atr_bps=55 --stress fee+10:10:0:0 --stress spread+10:0:0:10 --run-id donchian-20-10-btc-1h-2024-regime-atr-55 --mc-seed 42 --mc-resamples 1000`

## Arquivos alterados

Nenhum.

## Mapeamento SPEC → execução

| SPEC | Execução |
|---|---|
| dataset | `btcusdt_1h_20240705_20241231_binance_spot` |
| strategy | `DonchianBreakoutStrategy(20, 10, long_only=True)` |
| filter | `atr_regime:window=14:min_atr_bps=55` |
| custos | H.1 |

## Testes executados

- `pytest` full: 366 passed, 1 skipped.
- `scripts/validate_artifacts.py`: exit 0.

## Invariantes

ADR-0010; ADR-0019; ADR-0022; ADR-0011.

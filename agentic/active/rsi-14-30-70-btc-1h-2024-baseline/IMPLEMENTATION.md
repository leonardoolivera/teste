# IMPLEMENTATION.md — N.2 RSI 14/30/70 BTC 1h 2024

> Gate: **implementação**. Idêntico a N.1 — única diferença é `--dataset-id`.

## Estratégia

`RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=70.0, long_only=True)`
em [src/alpha_forge/strategies/families/rsi/strategy.py](../../src/alpha_forge/strategies/families/rsi/strategy.py).

## CLI

`alpha-forge validate --strategy rsi --rsi-period 14 --rsi-oversold 30
--rsi-overbought 70 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
--run-id rsi-14-30-70-btc-1h-2024-baseline ...`

## Testes

Mesma base de N.1: 366 passed, 1 skipped. Nenhum teste asset-específico.

## Arquivos alterados (por este piloto)

Nenhum. Reuso puro do código da N.1.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `--dataset-id btcusdt_1h_20240705_20241231_binance_spot` |
| §4–§5 | `RSIMeanReversionStrategy(14, 30, 70, long_only=True)` |
| §6–11-bis | custos H.1, budget padrão |
| §critério 3 | `--stress spread+10:0:0:10` |

## Invariantes herdados

- ADR-0010 monotonicity.
- ADR-0019 `fee+Δ ≡ spread+Δ`.
- ADR-0027 causalidade.

# IMPLEMENTATION.md — N.3 RSI 14/30/70 ETH 1h 2024

> Gate: **implementação**. Idêntico a N.1/N.2 — dataset ETH.

## Estratégia

`RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=70.0, long_only=True)`.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 14 --rsi-oversold 30
--rsi-overbought 70 --dataset-id ethusdt_1h_20240705_20241231_binance_spot
--run-id rsi-14-30-70-eth-1h-2024-baseline ...`

## Testes

366 passed, 1 skipped.

## Arquivos alterados (por este piloto)

Nenhum. Reuso puro do código da N.1.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `--dataset-id ethusdt_1h_20240705_20241231_binance_spot` |
| §4–§5 | `RSIMeanReversionStrategy(14, 30, 70, long_only=True)` |
| §6–11-bis | custos H.1, budget padrão |
| §critério 3 | `--stress spread+10:0:0:10` |

## Invariantes herdados

- ADR-0010; ADR-0019; ADR-0027.

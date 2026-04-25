# IMPLEMENTATION.md — O.2 RSI 21/35/65 BTC 1h 2024

> Gate: **implementação**. Zero código novo; reparametrização sobre N.2.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 21 --rsi-oversold 35
--rsi-overbought 65 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
--run-id rsi-21-35-65-btc-1h-2024-baseline ...`

## Arquivos alterados (por este piloto)

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `btcusdt_1h_20240705_20241231_binance_spot` |
| §4 | `RSIMeanReversionStrategy(period=21, oversold=35, overbought=65, long_only=True)` |
| §5 | midline 50 exit |
| §6–11-bis | custos H.1, budget padrão |
| §critério 3 | `--stress spread+10:0:0:10` |

## Testes

Suíte full: **366 passed, 1 skipped**.

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0027.

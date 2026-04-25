# IMPLEMENTATION.md — O.1 RSI 7/25/75 BTC 1h 2024

> Gate: **implementação**. Idêntico a N.2, reparametrizado. Zero código novo.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 7 --rsi-oversold 25
--rsi-overbought 75 --dataset-id btcusdt_1h_20240705_20241231_binance_spot
--run-id rsi-7-25-75-btc-1h-2024-baseline ...`

## Arquivos alterados (por este piloto)

Nenhum.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §2 | `btcusdt_1h_20240705_20241231_binance_spot` |
| §4 | `RSIMeanReversionStrategy(period=7, oversold=25, overbought=75, long_only=True)` |
| §5 | midline 50 exit (ADR-0027) |
| §6–11-bis | custos H.1, budget padrão |
| §critério 3 | `--stress spread+10:0:0:10` |

## Testes

Suíte full permanece **366 passed, 1 skipped** (piloto puro, zero delta em testes).

## Invariantes herdados

ADR-0010; ADR-0019; ADR-0027.

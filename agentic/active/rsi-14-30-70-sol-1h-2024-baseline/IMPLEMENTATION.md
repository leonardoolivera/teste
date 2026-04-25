# IMPLEMENTATION.md — N.1 RSI 14/30/70 SOL 1h 2024

> Gate: **implementação**. Família `rsi` já formalizada em ADR-0027. Reutiliza
> toda a pipeline da Série J — única diferença é `--strategy rsi`.

## Estratégia

`RSIMeanReversionStrategy(period=14, oversold=30.0, overbought=70.0,
long_only=True)` em [src/alpha_forge/strategies/families/rsi/strategy.py](../../src/alpha_forge/strategies/families/rsi/strategy.py).

- SMA smoothing sobre `closes.diff().iloc[1:]`, barra `t` ignorada.
- Entry edge-triggered: `rsi_now < 30 AND rsi_prev >= 30`.
- Exit edge-triggered: `rsi_now >= 50 AND rsi_prev < 50` (midline, ADR-0027).
- Warm-up `period + 3 = 17` barras.

## CLI

`alpha-forge validate --strategy rsi --rsi-period 14 --rsi-oversold 30
--rsi-overbought 70 --dataset-id solusdt_1h_20240705_20241231_binance_spot
--run-id rsi-14-30-70-sol-1h-2024-baseline --taker-fee-bps 5 ...`

## Testes

- 27 unit tests em [tests/unit/test_rsi_mean_reversion.py](../../tests/unit/test_rsi_mean_reversion.py).
- 1 property test causal em [tests/property/test_rsi_causal.py](../../tests/property/test_rsi_causal.py).
- 1 property test monotonicidade em [tests/property/test_cost_monotonicity_rsi.py](../../tests/property/test_cost_monotonicity_rsi.py).
- Suite full: **366 passed, 1 skipped** pós-integração CLI.

## Arquivos alterados (por este piloto)

Nenhum. Família `rsi` e CLI já entregues como pré-requisito protocolar (ADR-0027)
antes do piloto abrir. Piloto consome infraestrutura existente.

## Mapeamento SPEC → execução

| SPEC § | Execução |
| ------ | -------- |
| §1 (hipótese) | verificada via `run_backtest` + `walk_forward` + `cost_stress` sobre dataset J.1 |
| §2 (mercado) | `--dataset-id solusdt_1h_20240705_20241231_binance_spot` |
| §4 (entradas) | `RSIMeanReversionStrategy(period=14, oversold=30, overbought=70, long_only=True)` |
| §5 (saídas) | mesmo objeto; exit edge-triggered midline 50 hardcoded (ADR-0027) |
| §6–11-bis (custos/budget) | `--taker-fee-bps 5 --slippage-bps-per-notional 2 --spread-bps 0 --capital 10000 --fracao 0.1 --alavancagem 2.0` |
| §critério 3 | `--stress spread+10:0:0:10` |

## Invariantes herdados

- ADR-0010 monotonicity (property test RSI verde).
- ADR-0019 `fee+Δ ≡ spread+Δ` (verificado no BACKTEST).
- ADR-0027 causalidade (property test verde).

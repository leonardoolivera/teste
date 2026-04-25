# IMPLEMENTATION.md — Donchian 20/10 BTCUSDT 1h 180d (short-side)

> Gate ativo: **implementação**. **Gap zero** — quarto piloto exercitando protocolo sem código novo; `DonchianBreakoutStrategy(long_only=False)` já existe em `src/alpha_forge/strategies/families/donchian/strategy.py` sob ADR-0011 + ADR-0013.

## Arquivos alterados

**Nenhum** arquivo em `src/` foi alterado. Lógica já existia:

- Estratégia: [src/alpha_forge/strategies/families/donchian/strategy.py](../../../src/alpha_forge/strategies/families/donchian/strategy.py) — `DonchianBreakoutStrategy(entry_window=20, exit_window=10, long_only=False)` (ADR-0013).
- Custos: [src/alpha_forge/backtest/cost.py](../../../src/alpha_forge/backtest/cost.py) — mesmo `CostModel` de H.1/H.2a/H.2b.
- Sizing: [src/alpha_forge/risk/sizing.py](../../../src/alpha_forge/risk/sizing.py) — `fixed_fractional_position_sizing` (ADR-0004).
- Engine: [src/alpha_forge/backtest/engine.py](../../../src/alpha_forge/backtest/engine.py) — `run_backtest` (ADR-0002).
- Pipeline: [src/alpha_forge/cli/app.py](../../../src/alpha_forge/cli/app.py) — subcomando `validate` com flag `--no-long-only` (ADR-0016 + ADR-0017).
- Dataset: mesmo de H.1/H.2b — `btcusdt_1h_20250705_20251231_binance_spot`.

## Mapeamento SPEC → código

| SPEC §seção | Implementação |
|---|---|
| §1 Hipótese | N/A — hipótese enunciada no SPEC; código apenas executa. |
| §2 Mercado (BTCUSDT spot) | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot`. |
| §3 Timeframe (1h, 4320 barras) | Dataset já ingerido. |
| §4 Entradas (ENTER_LONG/ENTER_SHORT simétrico, ADR-0013) | `DonchianBreakoutStrategy.decide` em [strategy.py](../../../src/alpha_forge/strategies/families/donchian/strategy.py) — branch `long_only=False` emite ambos; empate → ENTER_SHORT. |
| §5 Saídas (reversal, sem EXIT explícito) | Fechamento via reversão coordenada pela engine (ADR-0012 reverse-on-signal, custo duplo). |
| §6 Stops (nenhum) | ADR-0013 preserva ausência de stops; sem branch de stop. |
| §7 Sizing (fracao=0.1, alav=2.0) | Flags CLI → `RiskBudget` → `fixed_fractional_position_sizing`. |
| §8 Fees (5bps taker) | `CostModel.taker_fee_bps` (ADR-0006). |
| §9 Slippage (2bps/unit_notional) | `CostModel.slippage_bps_per_unit_notional` (ADR-0006). |
| §10 Spread (0bps baseline) | `CostModel.spread_bps` (ADR-0019). Stress via `--stress spread+10:0:0:10`. |
| §11 Funding (N/A) | Spot. Limitação declarada em SPEC §13. |
| §12 Condições inválidas (warm-up 21, long_only=False) | Property-based de causalidade + `test_cost_monotonicity_donchian_short.py` cobrem. |
| §13 Limitações | N/A em código. |

## Decisões técnicas

- **Nenhum código novo.** Quarto piloto reusando código existente.
- **Flag `--no-long-only` usada pela primeira vez no protocolo agentic** — ativa short-side (ADR-0013). Gate anti-regressão: property-based `test_cost_monotonicity_donchian_short.py` já verde na suíte base.
- **Flags canonicalizadas no `run.json`** com `long_only=False` registrado.
- **Dispensa `PYTHONIOENCODING=utf-8`** (H.3 + fix ad-hoc de H.2b `_cmd_compare`).

## Gaps declarados

Nenhum.

## Comando canônico

```bash
python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['validate', '--run-id', 'donchian-20-10-btc-180d-short', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10', '--no-long-only', '--n-folds', '5', '--mc-resamples', '500', '--mc-seed', '42', '--stress', 'fee+10:10:0:0', '--stress', 'slip+5:0:5:0', '--stress', 'spread+10:0:0:10']))"
```

**Comando de comparação (gate 4 do piloto):**

```bash
python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['compare', 'donchian-20-10-btc-180d-baseline', 'donchian-20-10-btc-180d-short']))"
```

Segundo uso protocolar do subcomando `compare` — isola efeito do modo (long vs short) dentro da mesma family/asset/período.

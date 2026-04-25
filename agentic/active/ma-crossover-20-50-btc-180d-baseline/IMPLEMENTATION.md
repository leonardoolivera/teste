# IMPLEMENTATION.md — MA Crossover 20/50 BTCUSDT 1h 180d (baseline)

> Gate ativo: **implementação**. **Gap zero** — terceiro piloto exercitando protocolo sem código novo; `MovingAverageCrossoverStrategy` já existe em `src/alpha_forge/strategies/families/ma_crossover/strategy.py` sob ADR-0008 + ADR-0012.

## Arquivos alterados

**Nenhum** arquivo em `src/` foi alterado. Lógica já existia:

- Estratégia: [src/alpha_forge/strategies/families/ma_crossover/strategy.py](../../../src/alpha_forge/strategies/families/ma_crossover/strategy.py) — `MovingAverageCrossoverStrategy(short_window=20, long_window=50, long_only=True)` (ADR-0008 default).
- Custos: [src/alpha_forge/backtest/cost.py](../../../src/alpha_forge/backtest/cost.py) — mesmo `CostModel` de H.1/H.2a.
- Sizing: [src/alpha_forge/risk/sizing.py](../../../src/alpha_forge/risk/sizing.py) — `fixed_fractional_position_sizing` (ADR-0004).
- Engine: [src/alpha_forge/backtest/engine.py](../../../src/alpha_forge/backtest/engine.py) — `run_backtest` (ADR-0002).
- Pipeline: [src/alpha_forge/cli/app.py](../../../src/alpha_forge/cli/app.py) — subcomando `validate` (ADR-0016 + ADR-0017).
- Dataset: mesmo de H.1 — `btcusdt_1h_20250705_20251231_binance_spot`.

## Mapeamento SPEC → código

| SPEC §seção | Implementação |
|---|---|
| §1 Hipótese | N/A — hipótese é enunciada no SPEC; código apenas executa. |
| §2 Mercado (BTCUSDT spot) | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot`. |
| §3 Timeframe (1h, 4320 barras) | Dataset já ingerido. |
| §4 Entradas (cross-up SMA20/50) | `MovingAverageCrossoverStrategy.on_bar` em [strategy.py](../../../src/alpha_forge/strategies/families/ma_crossover/strategy.py) — ADR-0008 §Entradas. |
| §5 Saídas (cross-down SMA20/50) | Mesmo arquivo, ramo de exit. |
| §6 Stops (nenhum) | Confirmado: não há branch de stop em `strategy.py`. |
| §7 Sizing (fracao=0.1, alav=2.0) | Flags CLI → `RiskBudget` → `fixed_fractional_position_sizing`. |
| §8 Fees (5bps taker) | `CostModel.taker_fee_bps` (ADR-0006). |
| §9 Slippage (2bps/unit_notional) | `CostModel.slippage_bps_per_unit_notional` (ADR-0006). |
| §10 Spread (0bps baseline) | `CostModel.spread_bps` (ADR-0019). Stress via `--stress spread+10:0:0:10`. |
| §11 Funding (N/A) | Spot. |
| §12 Condições inválidas (warm-up 51) | Property-based de causalidade cobre warm-up = HOLD. `long_window + 1` barras iniciais. |
| §13 Limitações | N/A em código. |

## Decisões técnicas

- **Nenhum código novo.** Terceiro piloto reusando código existente.
- **Flags canonicalizadas no `run.json`.**
- **Dispensa `PYTHONIOENCODING=utf-8`** (H.3).
- **Comparação transversal com H.1 via `alpha-forge compare`** — subcomando read-only (ADR-0018); piloto documenta o diff em AUDIT.md.

## Gaps declarados

Nenhum.

## Comando canônico

```bash
python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['validate', '--run-id', 'ma-crossover-20-50-btc-180d-baseline', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--strategy', 'ma_crossover', '--short-window', '20', '--long-window', '50', '--n-folds', '5', '--mc-resamples', '500', '--mc-seed', '42', '--stress', 'fee+10:10:0:0', '--stress', 'slip+5:0:5:0', '--stress', 'spread+10:0:0:10']))"
```

**Comando de comparação (gate 4 do piloto):**

```bash
python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['compare', 'donchian-20-10-btc-180d-baseline', 'ma-crossover-20-50-btc-180d-baseline']))"
```

Primeiro uso real do subcomando `compare` dentro do protocolo agentic.

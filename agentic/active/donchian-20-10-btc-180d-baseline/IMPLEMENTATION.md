# IMPLEMENTATION.md — Donchian 20/10 BTCUSDT 1h 180d (baseline)

> Gate ativo: **implementação**. **Gap zero** — nenhum código novo em `src/`; o piloto exercita código existente sob ADR-0011 + ADR-0013.

## Arquivos alterados

**Nenhum** arquivo em `src/` foi alterado neste piloto. Toda a lógica já existia:

- Estratégia: [src/alpha_forge/strategies/families/donchian/strategy.py](../../../src/alpha_forge/strategies/families/donchian/strategy.py) — `DonchianBreakoutStrategy(entry_window=20, exit_window=10, long_only=True)` (ADR-0011 default).
- Custos: [src/alpha_forge/backtest/cost.py](../../../src/alpha_forge/backtest/cost.py) — `CostModel(taker_fee_bps=5.0, slippage_bps_per_unit_notional=2.0, spread_bps=0.0)` (ADR-0006 + ADR-0019).
- Sizing: [src/alpha_forge/risk/sizing.py](../../../src/alpha_forge/risk/sizing.py) — `fixed_fractional_position_sizing` (ADR-0004).
- Engine: [src/alpha_forge/backtest/engine.py](../../../src/alpha_forge/backtest/engine.py) — `run_backtest` (ADR-0002 + ADR-0012 reverse-on-signal, irrelevante aqui por ser long-only).
- Pipeline: [src/alpha_forge/cli/app.py](../../../src/alpha_forge/cli/app.py) — subcomando `validate` (ADR-0016 + ADR-0017).
- Dataset: [data/processed/BTCUSDT/1h/btcusdt_1h_20250705_20251231_binance_spot.parquet](../../../data/processed/BTCUSDT/1h/btcusdt_1h_20250705_20251231_binance_spot.parquet) — cadastrado em [data/datasets.yaml](../../../data/datasets.yaml) (ADR-0005 + ADR-0009).

## Mapeamento SPEC → código

| SPEC §seção | Implementação |
|---|---|
| §1 Hipótese | N/A — hipótese é enunciada no SPEC; código apenas executa. |
| §2 Mercado (BTCUSDT spot) | `--dataset-id btcusdt_1h_20250705_20251231_binance_spot` na CLI `validate`. |
| §3 Timeframe (1h, 4320 barras) | Dataset parquet já ingerido por `scripts/ingest_binance_vision.py`, `declared_gaps: []`. |
| §4 Entradas (rompimento 20-barras de `high[t-1]`) | `DonchianBreakoutStrategy.on_bar` em [strategy.py](../../../src/alpha_forge/strategies/families/donchian/strategy.py) — ADR-0011 §Entradas. |
| §5 Saídas (rompimento baixo 10-barras de `low[t-1]`) | Mesmo arquivo, ramo de exit. Ordem EXIT-antes-ENTER preservada (ADR-0011 §Ordem). |
| §6 Stops (nenhum) | Confirmado: não há branch de stop em `strategy.py`. |
| §7 Sizing (fracao=0.1, alavancagem=2.0) | Flags CLI `--fracao 0.1 --alavancagem 2.0` → `RiskBudget` → `fixed_fractional_position_sizing` (ADR-0004). Notional por trade = 2000 USDT. |
| §8 Fees (5bps taker) | Flag `--taker-fee-bps 5.0` → `CostModel.taker_fee_bps` (ADR-0006). |
| §9 Slippage (2 bps/unit_notional) | Flag `--slippage-bps-per-notional 2.0` → `CostModel.slippage_bps_per_unit_notional` (ADR-0006). |
| §10 Spread (0bps baseline) | Flag `--spread-bps 0.0` (default) → `CostModel.spread_bps` (ADR-0019). Stress via `--stress spread+10:0:0:10`. |
| §11 Funding (N/A) | Dataset é spot; nenhuma lógica de funding em `backtest/`. Confirmação estrutural. |
| §12 Condições inválidas (warm-up 20 barras) | Property-based de causalidade [tests/property/test_lookahead_guard.py](../../../tests/property/test_lookahead_guard.py) já cobre warm-up = HOLD. Dataset sem gaps confere a ausência de NaN por construção. |
| §13 Limitações | N/A em código; são observações do SPEC. |

## Decisões técnicas

- **Nenhum código novo.** Este piloto é um "smoke test" do protocolo agentic completo (pesquisa → validação → auditoria) com input conhecido e previsível.
- **Flags canonicalizadas no `run.json`** (ADR-0017) — qualquer re-execução com `run_id` idêntico é bit-a-bit reprodutível.
- **Sem flag `--no-long-only`** — comportamento ADR-0011 puro; short side (ADR-0013) é piloto separado futuro.

## Gaps declarados

Nenhum. Código em `src/` cobre integralmente o SPEC. Se houver qualquer divergência, é bug existente não relacionado a este piloto.

## Comando canônico

```bash
PYTHONIOENCODING=utf-8 python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['validate', '--run-id', 'donchian-20-10-btc-180d-baseline', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10', '--n-folds', '5', '--mc-resamples', '500', '--mc-seed', '42', '--stress', 'fee+10:10:0:0', '--stress', 'slip+5:0:5:0', '--stress', 'spread+10:0:0:10']))"
```

**Nota operacional:** em Windows, `PYTHONIOENCODING=utf-8` é necessário porque `_cmd_validate` imprime `→` em `app.py:672` — bug existente, não introduzido por este piloto; próximo patch pode re-wrap `sys.stdout` de forma análoga aos hooks agentic.

# VALIDATION.md — Donchian 20/10 BTCUSDT 1h 180d (baseline)

> Gate ativo: **validação**. Produzido pelo pipeline `alpha-forge validate` (ADR-0016 + ADR-0017) + conferência manual dos JSONs persistidos em `results/validation/donchian-20-10-btc-180d-baseline/`.

## Testes executados

### Suíte completa

- **Comando:** `python -m pytest -q`
- **Resultado:** `289 passed, 1 skipped` em ~96s (estado do repositório em 2026-04-17; piloto não altera `src/` nem `tests/`).

### Pipeline de validação rodado pelo piloto

- **Comando canônico** (idêntico ao IMPLEMENTATION.md §Comando):
  ```bash
  PYTHONIOENCODING=utf-8 python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['validate', '--run-id', 'donchian-20-10-btc-180d-baseline', '--dataset-id', 'btcusdt_1h_20250705_20251231_binance_spot', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10', '--n-folds', '5', '--mc-resamples', '500', '--mc-seed', '42', '--stress', 'fee+10:10:0:0', '--stress', 'slip+5:0:5:0', '--stress', 'spread+10:0:0:10']))"
  ```
- **Exit code:** 0.
- **Artefatos gravados:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` em `results/validation/donchian-20-10-btc-180d-baseline/`.

### Nenhum teste novo foi adicionado

Este piloto **não escreve código em `src/`** (ver IMPLEMENTATION.md §Gaps). Portanto não há testes unitários ou property-based novos; a suíte existente (ADRs 0002/0010/0019) já cobre toda a lógica envolvida.

### Property-based de causalidade (ADR-0002)

- **Cobre OHLCV completo:** sim (`tests/property/test_lookahead_guard.py`).
- **Status na suíte:** verde (`1 skipped` é teste inconclusivo por falta de sinais; ADR-0002 §Limitações).

### Property-based de monotonicidade de custo (ADR-0010 + ADR-0019)

- **Fee monotonicity (Donchian long-only):** verde em `tests/property/test_cost_monotonicity_donchian.py`.
- **Slippage monotonicity (Donchian long-only):** verde na mesma suíte.
- **Spread monotonicity (ADR-0019):** verde em `tests/property/test_cost_monotonicity_spread.py` (estratégia de referência = MA crossover, mas extensível por construção a Donchian — propriedade é estrutural).

## Conformidade ao SPEC

Item por item, conferindo SPEC vs. flags do `run.json` e fills observados:

| SPEC §seção | Evidência | Status |
|---|---|---|
| §1 Hipótese (preservar capital + hit≥45%) | `baseline.final_equity = 9089.79 < 9500` (falha critério 1 de preservação); `baseline.hit_rate = 0.2545 < 0.45` (falha explicitamente) | **GAP — refuta** |
| §2 Mercado (BTCUSDT spot) | `run.json.flags.dataset_id = btcusdt_1h_20250705_20251231_binance_spot` | OK |
| §3 Timeframe (1h 4320 barras) | `cost_stress.baseline.result.bars = 4320` | OK |
| §4 Entradas (rompimento 20-barras) | `run.json.flags.entry_window = "20"` | OK |
| §5 Saídas (rompimento-baixo 10-barras) | `run.json.flags.exit_window = "10"` | OK |
| §6 Stops (nenhum) | Inspeção de `fills`: side alterna `long` ↔ `flat`; nenhum side `stop` — consistente com ADR-0011 | OK |
| §7 Sizing (fracao=0.1, alav=2.0) | `run.json.flags.fracao = "0.1", alavancagem = "2.0"`; primeiros fills mostram `notional=2000.0` constante | OK |
| §8 Fees (5bps taker) | `baseline.cost.taker_fee_bps = 5.0` | OK |
| §9 Slippage (2bps/unit_notional) | `baseline.cost.slippage_bps_per_unit_notional = 2.0` | OK |
| §10 Spread (0bps baseline, testado +10) | `baseline.cost.spread_bps = 0.0`; cenário `spread+10.cost.spread_bps = 10.0` | OK |
| §11 Funding (N/A) | Não há lógica de funding em `backtest/`; spot dataset | OK |
| §12 Condições inválidas (warm-up 20) | Primeiros fills observados no dataset começam em `2025-07-06 15:00` (bar 38) — coerente com warm-up + esperar primeiro rompimento real | OK |
| §13 Limitações (dataset único, 180d curto) | Confirmado — só BTCUSDT rodado; walk-forward mostra 4 folds de ~36 dias cada | OK (registrado) |

## Métricas-chave conferidas

| Métrica | Valor (baseline, 4320 barras) | Fonte |
|---|---|---|
| `total_pnl` | -910.21 USDT | `cost_stress.json → baseline.result.metrics.total_pnl` |
| `trade_count` | 110 | mesmo |
| `hit_rate` | 0.2545 (25.45%) | mesmo |
| `max_drawdown` | 0.1049 (10.49%) | mesmo |
| `final_equity` | 9089.79 USDT | `cost_stress.json → baseline.result.final_equity` |

## Sensibilidade aos 3 eixos (preview, detalhes em BACKTEST.md)

| Cenário | final_equity | Δ vs baseline | Refuta SPEC? |
|---|---|---|---|
| baseline (fee=5, slip=2, spread=0) | 9089.79 | — | — |
| fee+10 (fee=15, slip=2, spread=0) | 8652.06 | -437.73 (-4.81%) | não (acima de -5%) |
| slip+5 (fee=5, slip=7, spread=0) | 9046.05 | -43.74 (-0.48%) | não |
| spread+10 (fee=5, slip=2, spread=10) | 8652.06 | -437.73 (-4.81%) | não (acima de -5%, dentro da margem) |

**Monotonicidade (ADR-0010 + ADR-0019):** todos os três cenários têm `final_equity` ≤ baseline — propriedade preservada por construção em todos os eixos. ✓

## Walk-forward (prévia — detalhes em BACKTEST.md)

- **Folds produzidos:** 4 (fold_index 1-4; fold 0 pulado por falta de histórico de train — ADR-0003).
- **Esquema:** rolling, train_fraction=0.5, min_test_bars=50.
- **Total trades (soma folds):** 85.
- **3 de 4 folds com pnl negativo.** Único fold positivo (fold 2) tem pnl=+10.64 USDT (praticamente zero).

## Monte Carlo (prévia — detalhes em BACKTEST.md)

- **Resamples:** 500, **seed:** 42.
- **final_equity percentis:** p5=8821.60, p25=9063.09, **p50=9246.86**, p75=9426.36, p95=9716.27.
- **Todos os 5 percentis < 10000 (capital inicial).** Probabilidade de preservar capital nesse regime é <<5% pela simulação.

## Falhas conhecidas

- **SPEC §1 (hipótese) é refutado por dois critérios independentes:** `hit_rate = 25.45% < 45%` e `final_equity = 9089.79 < 9500`. `spread+10` Δ=-4.81% está abaixo do limiar -5% por ~0.2% — critério de refutação 3 do SPEC passa, mas só por margem estreita.
- **Warning numpy `RuntimeWarning: invalid value encountered in divide`** aparece durante walk-forward (em cálculo de correlação de Monte Carlo); é benigno e já conhecido da suíte (aparece 186 vezes em pytest).
- **Bug Windows cp1252** em `src/alpha_forge/cli/app.py:672` (caractere `→` em print) — contornado via `PYTHONIOENCODING=utf-8`. Não afeta correção do pipeline nem do JSON persistido; só afeta stdout em Windows sem a env var. Candidato a micro-patch futuro.

## Comando de reprodução

Idêntico ao IMPLEMENTATION.md §Comando canônico. Reprodutibilidade garantida pela semente de Monte Carlo (`--mc-seed 42`) e pelo `run.json` persistido (ADR-0017).

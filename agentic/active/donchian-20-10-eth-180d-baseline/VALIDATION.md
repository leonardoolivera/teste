# VALIDATION.md — Donchian 20/10 ETHUSDT 1h 180d (baseline)

> Gate ativo: **validação**. Produzido pelo pipeline `alpha-forge validate` (ADR-0016 + ADR-0017) + conferência manual dos JSONs persistidos em `results/validation/donchian-20-10-eth-180d-baseline/`.

## Testes executados

### Suíte completa

- **Comando:** `python -m pytest -q`
- **Resultado:** `289 passed, 1 skipped` em ~97s (estado do repositório após H.3; piloto H.2a não altera `src/` nem `tests/`).

### Pipeline de validação rodado pelo piloto

- **Comando canônico** (idêntico ao IMPLEMENTATION.md §Comando; dispensa `PYTHONIOENCODING=utf-8` graças ao patch H.3):
  ```bash
  python -c "from alpha_forge.cli import app; import sys; sys.exit(app.run(['validate', '--run-id', 'donchian-20-10-eth-180d-baseline', '--dataset-id', 'ethusdt_1h_20250705_20251231_binance_spot', '--strategy', 'donchian', '--entry-window', '20', '--exit-window', '10', '--n-folds', '5', '--mc-resamples', '500', '--mc-seed', '42', '--stress', 'fee+10:10:0:0', '--stress', 'slip+5:0:5:0', '--stress', 'spread+10:0:0:10']))"
  ```
- **Exit code:** 0.
- **Artefatos gravados:** `run.json`, `walk_forward.json`, `monte_carlo.json`, `cost_stress.json` em `results/validation/donchian-20-10-eth-180d-baseline/`.

### Nenhum teste novo foi adicionado

Piloto **não escreve código em `src/`** (gap zero). Suíte existente (ADRs 0002/0010/0019) já cobre toda a lógica.

### Property-based de causalidade (ADR-0002)

- **Cobre OHLCV completo:** sim (`tests/property/test_lookahead_guard.py`).
- **Status na suíte:** verde.

### Property-based de monotonicidade de custo (ADR-0010 + ADR-0019)

- **Fee monotonicity (Donchian long-only):** verde em `tests/property/test_cost_monotonicity_donchian.py`.
- **Slippage monotonicity (Donchian long-only):** verde na mesma suíte.
- **Spread monotonicity (ADR-0019):** verde em `tests/property/test_cost_monotonicity_spread.py`.

## Conformidade ao SPEC

Item por item:

| SPEC §seção | Evidência | Status |
|---|---|---|
| §1 Hipótese (preservar capital + hit≥45%) | `baseline.final_equity = 10240.02 ≥ 9500` ✓ mas `baseline.hit_rate = 0.2813 < 0.45` ✗ | **GAP — refuta por hit_rate** |
| §2 Mercado (ETHUSDT spot) | `run.json.flags.dataset_id = ethusdt_1h_20250705_20251231_binance_spot` | OK |
| §3 Timeframe (1h 4320 barras) | `cost_stress.baseline.result.bars = 4320` | OK |
| §4 Entradas (rompimento 20-barras) | `run.json.flags.entry_window = "20"` | OK |
| §5 Saídas (rompimento-baixo 10-barras) | `run.json.flags.exit_window = "10"` | OK |
| §6 Stops (nenhum) | Inspeção de `fills`: side alterna `long` ↔ `flat`; nenhum side `stop` — consistente com ADR-0011 | OK |
| §7 Sizing (fracao=0.1, alav=2.0) | `run.json.flags.fracao = "0.1", alavancagem = "2.0"`; notional constante = 2000 USDT | OK |
| §8 Fees (5bps taker) | `baseline.cost.taker_fee_bps = 5.0` | OK |
| §9 Slippage (2bps/unit_notional) | `baseline.cost.slippage_bps_per_unit_notional = 2.0` | OK |
| §10 Spread (0bps baseline, testado +10) | `baseline.cost.spread_bps = 0.0`; cenário `spread+10.cost.spread_bps = 10.0` | OK |
| §11 Funding (N/A) | Spot dataset; sem funding em `backtest/` | OK |
| §12 Condições inválidas (warm-up 20) | Property-based cobre warm-up = HOLD | OK |
| §13 Limitações (dataset único ETH) | Confirmado — H.2a é single-asset vs H.1 BTC; comparação transversal em AUDIT.md | OK (registrado) |

## Métricas-chave conferidas

| Métrica | Valor (baseline, 4320 barras) | Fonte |
|---|---|---|
| `total_pnl` | +240.02 USDT | `cost_stress.json → baseline.result.metrics.total_pnl` |
| `trade_count` | 96 | mesmo |
| `hit_rate` | 0.2813 (28.13%) | mesmo |
| `max_drawdown` | 0.0890 (8.90%) | mesmo |
| `final_equity` | 10240.02 USDT | `cost_stress.json → baseline.result.final_equity` |

**Contraste com H.1 (BTC):** baseline ETH tem `final_equity > 10000` (+2.4%) enquanto BTC tinha -9.1%. Porém `hit_rate` de ambos está **abaixo** de 45% (ETH=28.13%, BTC=25.45%) — o critério 1 de refutação falha nos dois.

## Sensibilidade aos 3 eixos (preview, detalhes em BACKTEST.md)

| Cenário | final_equity | Δ vs baseline | Refuta SPEC? |
|---|---|---|---|
| baseline (fee=5, slip=2, spread=0) | 10240.02 | — | — |
| fee+10 (fee=15, slip=2, spread=0) | 9855.93 | -384.09 (-3.75%) | não (acima de -5%) |
| slip+5 (fee=5, slip=7, spread=0) | 10201.51 | -38.50 (-0.38%) | não |
| spread+10 (fee=5, slip=2, spread=10) | 9855.93 | -384.09 (-3.75%) | não (acima de -5%, ε = 1.25%) |

**Monotonicidade (ADR-0010 + ADR-0019):** todos os três cenários têm `final_equity` ≤ baseline — propriedade preservada. ✓

**Validação estrutural ADR-0019 (2ª vez, cross-asset):** `fee+10` e `spread+10` produzem **Δ idêntico** (-384.09 USDT; -3.75%) também em ETH — confirma empiricamente pela segunda vez que a propriedade é estrutural (independente de ativo), não coincidência.

## Walk-forward (prévia — detalhes em BACKTEST.md)

- **Folds produzidos:** 4 (fold_index 1-4; fold 0 pulado por falta de histórico de train — ADR-0003).
- **Esquema:** rolling, train_fraction=0.5, min_test_bars=50.
- **Total trades (soma folds):** 77.
- **1 de 4 folds com pnl positivo.** Fold 1 (+111.78 USDT, 16 trades, hit=37.5%); folds 2-4 negativos com magnitude crescente (-80.05, -204.82, -383.41).

**Contraste com H.1:** BTC teve 3/4 folds negativos; ETH tem 3/4 também negativos. Fold 1 de ETH é mais positivo que fold 2 de BTC (que era o único positivo de BTC com +10.64). Padrão temporal coerente: início da janela (agosto) teve algum edge residual; segunda metade degrada monotonicamente.

## Monte Carlo (prévia — detalhes em BACKTEST.md)

- **Resamples:** 500, **seed:** 42.
- **final_equity percentis:** p5=8651.16, p25=9115.52, **p50=9434.94**, p75=9749.60, p95=**10339.78**.
- **p95 > 10000** — diferentemente de H.1 (onde p95=9716.27 < 10000), em ETH a cauda superior do Monte Carlo **passa** breakeven. Probabilidade empírica de preservar capital nesse regime é 5-25% (entre p75 e p95; interpolação linear rough ≈ 17%).

## Falhas conhecidas

- **SPEC §1 (hipótese) é refutado por hit_rate isoladamente:** `hit_rate = 28.13% < 45%`. `final_equity = 10240.02 ≥ 9500` passa, mas não compensa — critério de refutação 1 é boolean.
- **Warning numpy `RuntimeWarning: invalid value encountered in divide`** aparece em cálculo de correlação do Monte Carlo; benigno e idêntico ao comportamento observado em H.1.
- **Bug cp1252 em `app.py`** foi **resolvido na Frente H.3** antes deste piloto — comando canônico H.2a roda sem `PYTHONIOENCODING=utf-8`.

## Comando de reprodução

Idêntico ao IMPLEMENTATION.md §Comando canônico. Reprodutibilidade garantida pela semente de Monte Carlo (`--mc-seed 42`) e pelo `run.json` persistido (ADR-0017).

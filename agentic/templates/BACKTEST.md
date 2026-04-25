# BACKTEST.md — {{NOME DA ESTRATÉGIA}}

> **Template.** Copie para `agentic/active/<slug>/BACKTEST.md` e preencha. Remova este bloco de nota ao finalizar.
> Produzido pelo `backtest-validator` após `VALIDATION.md` verde.

---

## Dataset

- **ID:** `{{dataset_id}}` (ex: `btcusdt_1h_20250705_20251231_binance_spot`).
- **Período:** {{YYYY-MM-DD a YYYY-MM-DD}}.
- **Barras:** {{N}}.
- **sha256:** {{do manifesto `data/datasets.yaml`}}.
- **Gaps declarados:** {{N}} (ver `data/datasets.yaml`).

## Período e recorte

{{Se houve recorte extra (ex: excluir primeiras 30 barras por warm-up), documentar aqui.}}

## Custos aplicados (ADR-0006 + ADR-0019)

- **Taker fee:** {{X}} bps.
- **Slippage:** {{Y}} bps por unidade de notional/capital_inicial.
- **Spread:** {{Z}} bps.

## Métricas (ADR-0007)

Rodadas pela CLI `alpha-forge run-demo`:

| Métrica | Valor |
|---|---|
| `total_pnl` | {{±N}} |
| `trade_count` | {{N}} |
| `hit_rate` | {{fração ou `None` se `trade_count=0`}} |
| `max_drawdown` | {{fração ∈ [0, 1]}} |
| `final_equity` | {{N}} |

## Sensibilidade via cost_stress (ADR-0014 + ADR-0019)

Rodada via `alpha-forge validate --stress ...`:

| Label | fee_delta | slip_delta | spread_delta | final_equity | delta vs baseline |
|---|---|---|---|---|---|
| `baseline` | 0 | 0 | 0 | {{N}} | 0 |
| `fee+10` | 10 | 0 | 0 | {{N}} | {{-N}} |
| `slip+5` | 0 | 5 | 0 | {{N}} | {{-N}} |
| `spread+10` | 0 | 0 | 10 | {{N}} | {{-N}} |

Monotonicidade ADR-0010 (estendida por ADR-0019 ao eixo spread) foi preservada em todos os cenários.

## Walk-forward (ADR-0003)

| Fold | Período test | trade_count | final_equity |
|---|---|---|---|
| 1 | {{...}} | {{N}} | {{N}} |
| 2 | {{...}} | {{N}} | {{N}} |
| ... | ... | ... | ... |

## Monte Carlo (ADR-0003)

- **Resamples:** {{N}}.
- **Seed:** {{int}}.
- **Percentis finais (p5/p25/p50/p75/p95):** {{...}}.
- **Max drawdown original:** {{N}}.

## Robustez multi-asset

{{Se rodou em múltiplos datasets (BTC/ETH/SOL), reportar estabilidade por símbolo.}}

| Symbol | final_equity | trade_count | hit_rate |
|---|---|---|---|
| BTCUSDT | {{N}} | {{N}} | {{N}} |
| ETHUSDT | {{N}} | {{N}} | {{N}} |
| SOLUSDT | {{N}} | {{N}} | {{N}} |

## Lookahead bias

- Property-based de causalidade verde: {{sim/não}}.
- Coverage de OHLCV: {{completo/parcial}}.
- Guardião de causalidade (ADR-0002): {{evidência}}.

## Persistência

- **Artefatos gravados em:** `results/validation/{{slug}}/`.
- `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` (ADR-0015 + ADR-0017).

## Notas

{{Achados factuais, sem juízo promocional. "Trade count baixo", "hit rate modesto", "regime-dependente em X", etc.}}

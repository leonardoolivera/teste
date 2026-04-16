# decisions/

Architecture Decision Records. One decision per file. Immutable once committed.

## Format

`NNNN-short-slug.md` — sequential number, lowercase, dash-separated.

Examples:
- `0001-use-django-over-fastapi.md`
- `0002-postgres-not-mongo.md`
- `0003-token-auth-not-jwt.md`

## Rules

1. **Never edit an ADR after it is merged.** If a decision is revisited, write a new ADR that supersedes it, and mark the old one as superseded at the top.
2. **One decision per file.** If you're bundling two decisions, split them.
3. **Keep ADRs short.** One page is usually too long. Half a page is often right.
4. **Write the ADR before or during the change, not after.** An ADR written weeks later is a rationalization.

## Template

See [`_TEMPLATE.md`](./_TEMPLATE.md). Copy it, renumber, rename.

## Index

_(Keep this list sorted and up to date. One line per ADR.)_

- [0001 — Foundational stack and architecture](./0001-foundational-stack-and-architecture.md) — Python 3.12 + vectorbt + 7 módulos com acoplamento frouxo; src-layout; uv/ruff/pyright/pytest; deploy local WSL2/Linux/macOS.
- [0002 — Anti-lookahead as infrastructure](./0002-anti-lookahead-as-infrastructure.md) — ordem temporal estrita + guardião de causalidade como infra + teste property-based obrigatório; motor próprio no núcleo mínimo é tática inicial, compatível com direção vectorbt.
- [0004 — Minimal risk policy](./0004-minimal-risk-policy.md) — núcleo mínimo só tem `RiskBudget` e `fixed_fractional_position_sizing`; sem sizing por volatilidade, sem equity guard, sem composite budgets.
- [0005 — Dataset versioning and manifest](./0005-dataset-versioning-and-manifest.md) — Parquet em `data/processed/` + manifesto `data/datasets.yaml` com sha256 e gaps declarados; `dataset_id` imutável; gap não declarado bloqueia carregamento.
- [0006 — Minimal execution cost model](./0006-minimal-execution-cost-model.md) — `CostModel` com taker fee em bps + slippage linear por notional/capital; aplicado no preço de execução; argumento obrigatório em `run_backtest`; sem maker/funding/spread nesta fase.
- [0007 — Minimal backtest metrics](./0007-minimal-backtest-metrics.md) — `BacktestMetrics` com `total_pnl`, `trade_count`, `hit_rate` (`None` quando sem trades) e `max_drawdown` (fração); vive em `backtest/metrics.py`; `ranking/scoring/` fica para depois.
- [0008 — First real strategy: causal MA crossover (long-only)](./0008-first-real-strategy-ma-crossover.md) — SMA curta × SMA longa sobre `close`; entrada em cruzamento para cima, saída em cruzamento para baixo; long-only; warm-up = `HOLD` até `long_window + 1` barras; stateless; sem stops/targets/filtros nesta fase.
- [0009 — First real dataset: BTC/USDT 1h, 180 days, Binance Vision dumps](./0009-first-real-dataset-binance-vision.md) — Binance Vision ZIPs mensais (sem `ccxt`); recorte inicial `btcusdt_1h_20250705_20251231_binance_spot`; multi-asset **por design** (nenhum hardcode de símbolo em `src/`); script de ingestão multi-símbolo desde o dia 1; gaps reais declarados um a um com razão factual; teto de 3 gaps / 48h.
- [0010 — Property-based test: cost monotonicity](./0010-cost-monotonicity-property-test.md) — `hypothesis` sobre `run_backtest`: fixado o cenário, se `cost_high ≥ cost_low` componente a componente e `trade_count > 0`, então `final_equity_high ≤ final_equity_low + tolerance`. Só em `final_equity`; fills podem divergir; estratégia de referência = MA crossover 20/50 sobre sintético seminal.
- [0011 — Donchian breakout strategy (long-only)](./0011-donchian-breakout-strategy.md) — breakout assimétrico em `high[t-1]`/`low[t-1]` sobre janelas independentes (`entry_window` default 20, `exit_window` default 10); long-only; stateless; EXIT avaliado antes de ENTER_LONG; redução a no-op por sinais redundantes é responsabilidade do engine; caracterização inicial em dataset real é observação, não validação.

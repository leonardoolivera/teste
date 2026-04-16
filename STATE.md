# STATE.md

> **What this file is:** the only document that reflects the current state of the project. Update it at the end of every work session.
>
> **What this file is NOT:** a description of goals, architecture, or decisions. Those live in `vision/` and `decisions/`. This file answers only: *where are we right now?*

---

## Current phase

`building` — **núcleo mínimo + custos + métricas + primeira estratégia real + primeiro dataset real + property-based de monotonicidade de custo implementados, validados e documentados em `system/`** (scaffolding + ADR-0001/0002/0004/0005/0006/0007/0008/0009/0010 → io/paths + data + risk + backtest causal com `CostModel` obrigatório + `Trade` fechado + `BacktestMetrics` + `MovingAverageCrossoverStrategy` + `DummyAlternatingStrategy` como sanidade + CLI `run-demo` com seletor de estratégia + `scripts/ingest_binance_vision.py` multi-símbolo + dataset real BTCUSDT 1h 180d + property-based garantindo `custo_maior ⇒ final_equity_menor`). Aguardando **direção do usuário** para a próxima frente.

<!--
empty:         no code yet, vision/ files are empty or partial
interviewing:  agent is asking the user to fill in vision/ files
scaffolding:   first ADR written, repo structure being created
building:      active feature development
stabilizing:   feature complete, bug fixing and polish
maintaining:   shipped, small changes only
-->

## What was last delivered

**ADRs 0009 e 0010 implementadas em bloco: primeiro dataset real (BTCUSDT 1h, 180 dias, Binance Vision) + property-based de monotonicidade de custo.** Seis guardrails operacionais explícitos do usuário respeitados integralmente: (1) símbolo canônico único normalizado na entrada do script; (2) `timezone` e `source` obrigatórios no manifesto; (3) gap declarado ou falha — rejeição bloqueia ingestão sem deixar Parquet órfão; (4) script multi-símbolo real desde o dia 1 (nenhum ramo `if symbol == "BTCUSDT"`); (5) código de rede isolado no script (`src/` não importa `urllib`/`ssl`/`certifi`); (6) nenhuma maquiagem — dataset real veio limpo e isso foi reportado como tal, não disfarçado. Delta entregue:

- `decisions/0009-first-real-dataset-binance-vision.md` (Accepted) — Binance Vision ZIPs mensais (sem `ccxt`, sem credenciais); recorte inicial BTCUSDT 1h 2025-07-05 → 2025-12-31; §2-bis (multi-asset como requisito de primeira classe, 5 invariantes estruturais) e §2-ter (próximo lote BTC+ETH+SOL 1h); teto de 3 gaps / 48h; gate anti-hardcode visando `src/` runtime.
- `decisions/0010-cost-monotonicity-property-test.md` (Accepted) — invariante: fixado o cenário, se `cost_high ≥ cost_low` componente a componente com ≥1 desigualdade estrita e `trade_count > 0`, então `final_equity_high ≤ final_equity_low + tol`. Só em `final_equity` (não `hit_rate`, não `max_drawdown` — não-monotônicas por efeito de ordem). Estratégia de referência MA 20/50 sobre sintético seminal.
- `scripts/ingest_binance_vision.py` — download mensal via `urllib` + `certifi` (SSL explícito); normalização canônica na entrada; detecção de gap contra grade do timeframe; upsert no manifesto preservando outras entradas; resumo por símbolo com `symbol`, `timeframe`, `window`, `bars_saved`, `gaps_detected`, `dataset_id`, `sha256`, `status`, `note`.
- `tests/unit/test_paths_multi_asset.py` — 4 testes provando que `processed_dataset_path` trata `symbol`/`timeframe` como opacos (BTCUSDT, ETHUSDT, SOLUSDT, BTC_USDT todos geram paths distintos sem qualquer privilégio de ativo).
- `tests/unit/test_data_loader.py::test_loader_multi_asset_nao_colide` — dois datasets de símbolos distintos coexistem no manifesto e carregam independentemente via `load_dataset(dataset_id)`.
- `tests/unit/test_ingest_binance_vision.py` — 4 testes sem rede (stubs para `download_if_missing` e `read_zip_as_frame`): normalização canônica; dois símbolos distintos não colidem (paths/sha256/manifesto distintos); gap não declarado rejeita e não deixa Parquet órfão; gap declarado passa.
- `tests/property/test_cost_monotonicity.py` — implementa ADR-0010 com os três guardrails específicos: (a) `cost_low`/`cost_high` nomeados explicitamente com helper `_dominates` atestando dominância componente a componente; (b) `FINAL_EQUITY_TOLERANCE` constante nomeada no topo do arquivo com razão (`1e-6 * REFERENCE_CAPITAL`); (c) mensagem de falha rica com cost_low, cost_high, final_equity_low/high, delta vs tolerance, trade_count_low/high, fills_low/high. `@settings(max_examples=30)`, 30 exemplos × 2 backtests de 720 barras em ~18s.
- `tests/integration/test_first_real_dataset.py` — roda MA 20/50 sobre o Parquet real; skip limpo se o arquivo ainda não foi ingerido (ambiente fresco).
- `data/datasets.yaml` populado com `btcusdt_1h_20250705_20251231_binance_spot`: 4320 barras 1h, `sha256=228249e2ceb7239e5ecb31aa1093614fe5fd9d72a8c5cec2c0f90ebaec7a973f`, zero gaps detectados, `source: binance_vision_spot`, `timezone: UTC`.
- `system/domain.md`, `system/api.md`, `system/flows.md` atualizados com: novo dataset cadastrado, script de ingestão como interface operacional, novos fluxos (ingestão Binance Vision com saída real 4320 barras/0 gaps; monotonicidade de custo property-based).

**Gate anti-hardcode:** `rg -n 'BTC(USDT)?' src/` → 0 matches. O runtime permanece agnóstico a símbolo.

**Resultado da suíte pós-entrega:** `66 passed, 1 skipped` (o skip é estrutural do hypothesis, by design). Partiu de `55 passed, 1 skipped` (após ADR-0008); ganhou 11 testes novos sem quebrar nenhum anterior. Property-based de monotonicidade reexecutado 3 vezes consecutivas sem flakiness (~18s cada).

**Dataset real caracterizado:** BTCUSDT 1h 2025-07-05 → 2025-12-31, 4320 barras, close ∈ [82.207, 126.011] USD (janela bull prolongada, top em torno de 126k). Janela entrou sem gaps — o laboratório registra isso como achado, não como conveniência.

### Entrega anterior (ADR-0008) — mantida

**ADR-0008 (primeira estratégia real — MA crossover causal long-only) implementada e integrada ao núcleo, saindo da dummy sem antecipar `validation/`, `ranking/` ou `regimes/`.** Três guardrails adicionais pedidos pelo usuário foram respeitados: (1) validação de parâmetros falha cedo e ruidosamente (`TypeError`/`ValueError`); (2) nenhum tratamento "inteligente" para janela insuficiente no cálculo da SMA — warm-up é `HOLD` explícito, sem `fillna`; (3) `ma_crossover` virou default na CLI, mas a `DummyAlternatingStrategy` continua acessível via `--strategy dummy`. Delta entregue:

- `decisions/0008-first-real-strategy-ma-crossover.md` — aprovada pelo usuário antes do código. Fixa contrato, definição exata de cruzamento, warm-up, separação estratégia×engine e critério de sucesso da fase.
- `src/alpha_forge/strategies/families/ma_crossover/__init__.py` + `strategy.py` — `MovingAverageCrossoverStrategy(short_window, long_window)`. SMA sobre `close`; stateless (`decide(window) -> Signal` é função pura de `window` e parâmetros); emite apenas `ENTER_LONG`, `EXIT`, `HOLD` (long-only). Validação cedo em `__init__`: `TypeError` para não-inteiros (inclui `bool`); `ValueError` para inteiros não positivos ou `short_window >= long_window`.
- `src/alpha_forge/cli/app.py` — novas flags: `--strategy {ma_crossover,dummy}` (default `ma_crossover`), `--short-window` (default 20), `--long-window` (default 50). Summary imprime linha `strategy: <name> short=... long=...`.
- Testes novos: `tests/unit/test_ma_crossover.py` (valida parâmetros, warm-up, cruzamento para cima, cruzamento para baixo, empate exato, long-only em cenário de queda, stateless); `tests/property/test_ma_crossover_causal.py` (hypothesis: mutar barra futura nunca altera sinal em `t`).
- `system/domain.md`, `system/api.md`, `system/flows.md` atualizados com a nova estratégia, nova flag, novos outputs do `run-demo` (MA crossover com custo × sem custo × dummy baseline) e novo fluxo de causalidade property-based.

**Resultado da suíte:** `55 passed, 1 skipped` (skip estrutural do hypothesis, by design). 20 testes novos entraram sem quebrar nenhum dos anteriores.

**Resultado do `run-demo`** sobre dataset sintético seminal (capital 10.000, fração 0.1, alavancagem 2x):

| Cenário | fills | trades | hit_rate | total_pnl | max_drawdown |
|---|---|---|---|---|---|
| `ma_crossover 20/50`, custo padrão | 16 | 8 | 12.50% | −464.64 (−4.65%) | 5.46% |
| `ma_crossover 20/50`, zero cost | 16 | 8 | 12.50% | −447.87 (−4.48%) | 5.37% |
| `dummy`, custo padrão | 479 | 239 | 32.22% | −21.72 (−0.22%) | 6.72% |

MA long-only sobre série sintética com drift baixo (0.0002) e ruído Gaussiano é estruturalmente perdedora — o projeto é honesto sobre isso (ADR-0008 §8: "objetivo desta estratégia não é ser boa"). Custo morde ~17 bps de PnL em 8 trades; com 16 fills, o impacto é muito menor do que na dummy (239 trades), que é outro dado útil — MA trade menos e paga menos atrito.

### Entrega anterior (ADRs 0006/0007) — mantida

**ADR-0006 (custos) + ADR-0007 (métricas) implementados e integrados ao núcleo.** Zero desvio de escopo: cost_model é argumento obrigatório de `run_backtest` (sem default silencioso); `hit_rate` é `None` quando não há trades (nunca `NaN`); nenhuma métrica além das quatro mínimas. Delta entregue:

- `decisions/0006-minimal-execution-cost-model.md` + `decisions/0007-minimal-backtest-metrics.md` — ambos aprovados integralmente pelo usuário antes do código.
- `src/alpha_forge/backtest/cost.py` — `CostModel` (pydantic frozen, `taker_fee_bps ≥ 0`, `slippage_bps_per_unit_notional ≥ 0`), `zero_cost()` explícito, `apply_cost` puro ajustando preço **contra o trader** em entrada e saída (entrada long / saída short pagam mais caro; saída long / entrada short recebem mais barato).
- `src/alpha_forge/backtest/schemas.py` — adicionados `Trade` (par fechado com `pnl` pós-custo) e `BacktestMetrics` (`total_pnl: float`, `trade_count: int ≥ 0`, `hit_rate: float | None`, `max_drawdown ∈ [0, 1]`). `BacktestResult` estendido com `trades: list[Trade]` e `metrics: BacktestMetrics | None`.
- `src/alpha_forge/backtest/metrics.py` — `compute_metrics(result, capital_inicial)` vive em `backtest/`, **não** em `ranking/scoring/` (ADR-0007: caracterização ≠ comparação).
- `src/alpha_forge/backtest/engine.py` — assinatura nova `run_backtest(*, prices, strategy, budget, cost_model, dataset_id)`; loop agora registra `Trade` no fechamento de posição com PnL já ajustado por custo; `compute_metrics` chamado obrigatoriamente no fim. Equity = `capital + PnL_realizado_dos_trades_fechados + PnL_unrealized_da_posicao_aberta`.
- `src/alpha_forge/cli/app.py` — flags novas: `--taker-fee-bps` (default 5.0), `--slippage-bps-per-notional` (default 2.0); bloco `--- metrics ---` no summary imprimindo as quatro métricas (`hit_rate` como `"N/A"` quando `None`).
- Testes novos: `tests/unit/test_cost_model.py` (8 — validação rejeita negativos; `zero_cost` não altera preço; custo contra o trader em 4 direções; slippage linear com notional; notional = capital paga taker + slippage integral), `tests/unit/test_backtest_metrics.py` (5 — zero trades → `hit_rate None`; equity flat; drawdown com curva conhecida; `hit_rate` com 3 trades rotulados; posição aberta no fim não conta como trade).
- Testes atualizados: `tests/unit/test_engine_reject_invalid_sizing.py` e `tests/integration/test_minimal_flow.py` passam `cost_model=zero_cost()` / `CostModel(5.0, 2.0)` e o integration test valida `metrics is not None`, `hit_rate` coerente com `trade_count`, `0 ≤ max_drawdown ≤ 1`.
- `system/domain.md`, `system/flows.md`, `system/api.md` — atualizados. `flows.md` contém output real do `run-demo` com custo padrão **e** com custo zero explícito; diferença quantifica o atrito aplicado pelo `CostModel` sobre a mesma estratégia.

**Resultado da suíte:** `35 passed, 1 skipped` (skip estrutural do hypothesis, por design).

**Resultado do `run-demo`** sobre dataset sintético seminal, capital 10.000, fração 0.1, alavancagem 2x:

- **Com custo padrão** (`taker_fee_bps=5.0`, `slippage_bps_per_notional=2.0`):
  ```
  equity final : 9978.28   total_pnl : -21.72 (-0.22%)
  trade_count  : 239       hit_rate  : 32.22%    max_drawdown : 6.72%
  ```
- **Com zero custo** (mesmo dataset e budget):
  ```
  equity final : 10495.60  total_pnl : +495.60 (+4.96%)
  trade_count  : 239       hit_rate  : 34.73%    max_drawdown : 4.51%
  ```

O custo **morde** como esperado: a mesma estratégia passa de `+4.96%` bruto para `-0.22%` líquido. Isso confirma que `apply_cost` é sentido pelo PnL final e que hit_rate e drawdown são sensíveis ao atrito.

### Entrega anterior (núcleo mínimo) — mantida

**Núcleo mínimo funcional**, obedecendo ADR-0001/0002/0004/0005. Zero desvio de escopo: nada de vectorbt, nada de validation/ranking/regimes. Sequência entregue:

- `src/alpha_forge/io/paths.py` — resolução canônica de paths (project_root, data/processed, manifesto, results).
- `src/alpha_forge/data/schemas.py` — `OHLCVBar`, `GapRecord`, `DatasetManifest` (pydantic v2, frozen, validators).
- `src/alpha_forge/data/synthetic.py` — `generate_ohlcv` determinístico (seed fixa; drift/vol/volume reproduzíveis).
- `src/alpha_forge/data/loaders.py` — `load_dataset` valida sha256 + janela + row_count + continuidade temporal contra `declared_gaps`; gap não declarado → `DatasetIntegrityError`.
- `scripts/bootstrap_synthetic_dataset.py` — gera o dataset seminal `synthetic_btcusdt_1h_seed42` (720 barras 1h) e atualiza `data/datasets.yaml` com todos os campos exigidos por ADR-0005.
- `src/alpha_forge/risk/schemas.py` — `RiskBudget` com hard cap 10x.
- `src/alpha_forge/risk/sizing.py` — `fixed_fractional_position_sizing` (função pura; sem I/O; sem estado).
- `src/alpha_forge/backtest/schemas.py` — `Side`, `Signal` (ENTER_LONG/ENTER_SHORT/EXIT/HOLD), `Fill`, `Rejection` com `RejectionReason`, `BacktestResult`.
- `src/alpha_forge/backtest/lookahead_guard.py` — `assert_causal` (heurística de hit-rate + correlação com retorno futuro); `LookaheadViolation`.
- `src/alpha_forge/backtest/engine.py` — loop causal explícito; Contrato A (janela = `prices[:t+1]`); execução em `t+1 open`; `assert_causal` obrigatório; rejeição determinística para zero/negativo/NaN/inf/acima-do-cap.
- `src/alpha_forge/strategies/base.py` — `Strategy` ABC com `decide(window) -> Signal`.
- `src/alpha_forge/strategies/families/dummy/strategy.py` — `DummyAlternatingStrategy` (compara duas últimas closes, emite EXIT ao inverter direção).
- `src/alpha_forge/cli/app.py` — casca fina com subcomando `run-demo`.
- Testes: `tests/unit/test_risk_sizing.py` (11), `tests/unit/test_engine_reject_invalid_sizing.py` (5 gatilhos), `tests/unit/test_data_loader.py` (gap declarado/não declarado, sha divergente), `tests/property/test_lookahead_guard.py` (hypothesis — aceita causal, rejeita peek), `tests/integration/test_minimal_flow.py` (pipeline completo).

### Entrega anterior (ADRs 0005/0002/0004) — mantida

**ADRs precursores do núcleo mínimo (0005, 0002, 0004) escritos em bloco antes de qualquer implementação**, conforme opção 2 aprovada pelo usuário. Escopo dos três deliberadamente reduzido ao que o núcleo mínimo precisa; expansões viram ADRs futuras:

- **ADR-0005 — Versionamento e manifesto de datasets.** Parquet em `data/processed/<symbol>/<timeframe>/<id>.parquet`; manifesto `data/datasets.yaml` com `id`, `symbol`, `timeframe`, `exchange`, `start`, `end`, `rows`, `source`, `sha256`, `gaps`; `dataset_id` imutável; gap não declarado bloqueia carregamento.
- **ADR-0002 — Anti-lookahead como infraestrutura.** Ordem temporal estrita (sinal em `t`, execução em `t+1` open); `backtest/lookahead_guard.py::assert_causal` chamado obrigatoriamente pelo engine; teste property-based com `hypothesis` obrigatório. Explicitamente declarado: motor próprio do núcleo mínimo é **escolha tática inicial** compatível com a direção macro de ADR-0001 para vectorbt, **não substituição silenciosa**.
- **ADR-0004 — Política mínima de risco.** `risk/` só contém `RiskBudget` (capital/fração/alavancagem ≤ 10x) + `fixed_fractional_position_sizing`. Explicitamente fora desta fase: volatility sizing, composite budgets, aggregate risk, equity/ruin guard, funding cost, margin simulation — cada um vira follow-up de ADR-0007.

Índice [`decisions/README.md`](./decisions/README.md) atualizado com os três.

**Entrega anterior (scaffolding) permanece válida:** `pyproject.toml`, `.python-version`, `.gitignore`, `src/alpha_forge/` (9 subpastas com `__init__.py` + README de 4 pontos, único código: `__version__` e placeholder de CLI), `tests/{unit,integration,property,fixtures}/` com smoke test, `configs/`, `notebooks/`, `data/`, `results/`, `.github/workflows/ci.yml`, `system/*.md` honestos, `playbooks/setup.md`, `README.md` raiz. Zero código de domínio.

Arquivos/árvore entregues:

- **Metadata:** `pyproject.toml` (deps da stack aprovada + ruff + pyright + pytest config), `.python-version` pinando 3.12, `.gitignore` cobrindo `data/`, `results/`, `.env`, caches, dist, checkpoints de Jupyter.
- **Pacote:** `src/alpha_forge/` com 9 subpastas (`data`, `strategies`, `strategies/families`, `regimes`, `risk`, `backtest`, `validation`, `ranking`, `ranking/scoring`, `ranking/reporting`, `cli`, `io`), cada uma com `__init__.py` vazio e `README.md` de 4 pontos (responsabilidade / o que ainda não existe / dependências / primeiro arquivo esperado). Único código executável: `alpha_forge.__version__` e `alpha_forge.cli.main()` placeholder.
- **Testes:** `tests/{unit,integration,property,fixtures}/` com READMEs + `conftest.py` + smoke test único (`tests/unit/test_smoke.py::test_package_imports`).
- **Configs:** `configs/{strategies,experiments,risk,regimes}/` com `.gitkeep` e README raiz descrevendo regras.
- **Notebooks:** `notebooks/{exploratory,reports}/` com `.gitkeep` e README.
- **Data/Results:** `data/{raw,processed}/`, `results/{runs,validation,rankings}/` com `.gitkeep`, README e `data/datasets.yaml` vazio (manifesto versionável).
- **CI:** `.github/workflows/ci.yml` mínimo (ruff + ruff format + pyright + pytest).
- **System (realidade):** `system/domain.md`, `system/api.md`, `system/flows.md` reescritos honestamente — "nada implementado" + fluxos de infra (smoke test, CI).
- **Playbook:** `playbooks/setup.md` reescrito para o projeto real.
- **README:** raiz reescrito com estado, ordem de leitura, três camadas, setup resumido, princípios.

Nada de inventar lógica de estratégia, risco ou backtest — apenas esqueleto, contratos mínimos e documentação coerente com `vision/` e `STATE.md`, conforme autorizado.

### Atualização documental de `system/` (pós-revisão)

Após aprovação do núcleo mínimo, os três arquivos da camada **Reality** foram reescritos para espelhar exatamente o código que existe hoje:

- [`system/domain.md`](./system/domain.md) — entidades implementadas (`OHLCVBar`, `GapRecord`, `DatasetManifest`, `RiskBudget`, `Signal`, `Side`, `Fill`, `Rejection`, `BacktestResult`, `Strategy` ABC, `DummyAlternatingStrategy`), invariantes estruturais, dataset seminal, e seção explícita do "o que ainda não existe".
- [`system/flows.md`](./system/flows.md) — fluxos reais: `alpha-forge run-demo` end-to-end, bootstrap do sintético, detecção de violação de causalidade, rejeição determinística, smoke test, CI. Cada fluxo cita o teste que o exercita.
- [`system/api.md`](./system/api.md) — API operacional interna: CLI, módulos públicos com assinaturas, invariantes aplicadas estruturalmente, interfaces deferred.

Blocker documental resolvido.

## What is pending

- **Próxima frente candidata (aguardando direção do usuário):** segunda estratégia simples-mas-real (preferência declarada do usuário por **Donchian breakout** antes de RSI). Abrir ADR-0011 curta fixando: janela do breakout, regra exata de entrada/saída, long-only nesta fase, warm-up explícito, causalidade por construção. Ao entrar, replicar o property-based de monotonicidade de custo no novo ADR (teste paralelo, não parametrização — cada estratégia explícita).
- **Alternativas que o usuário pode priorizar:** (a) short side da `MovingAverageCrossoverStrategy` (ADR derivada da 0008); (b) ingestão do próximo lote de ativos ETHUSDT + SOLUSDT 1h (mesma janela de BTC) para começar a exercitar a transversalidade multi-asset do pipeline sem abrir ADR; (c) observabilidade de backtest (quinta direção guardada pelo usuário: logging estruturado de fills/rejections/trades para permitir diagnóstico sem ler stdout).
- **Segurado (não abrir ainda):** `validation`, `ranking`, `regimes`, `vectorbt` como engine, `ccxt`, qualquer coisa parecida com produção live.
- **ADRs futuras:** ADR-0011 (Donchian breakout, candidata imediata); ADR-0003 (validação, walk-forward / monte carlo); ADR de ranking multiobjetivo; ADR de risco completo (volatility sizing/equity guard/aggregate); ADR de custos avançados (maker/funding/spread); ADR específica para short side da MA.
- **Playbook `playbooks/setup.md`** ainda com `# DRAFT — untested`. Implementação atual foi validada com `pip install --user -e .` em Python 3.13/Windows, não com `uv` em WSL2.
- Calibrar na fase `building` as duas metas TBD (pipeline end-to-end < 10 min; grid search ≥ 1.000 combinações < 2 h).

## Next step (exactly one)

**Aguardar direção do usuário para escolher a próxima frente** entre: (i) ADR-0011 + Donchian breakout (preferência declarada); (ii) short side da MA crossover; (iii) ingestão do próximo lote ETH/SOL 1h; (iv) observabilidade de backtest. Qualquer uma delas (exceto (iii), que é operacional) começa com ADR curta e fechada, no mesmo estilo das anteriores.

**Acceptance criteria for this step:**

- Usuário escolhe explicitamente a próxima frente (ou redireciona para outra).
- Se a frente escolhida for mudança de contrato ou estratégia nova: começa por ADR (escopo curto, decisão explícita, o que fica de fora), nunca por código.
- Manter segurado: `validation`, `ranking`, `regimes`, `vectorbt`, `ccxt`.

## Blockers

- **Aguardando escolha do usuário** entre as quatro frentes candidatas listadas acima.
- **TBD — calibrar na fase `building`:** alvo "pipeline end-to-end < 10 min" em `vision/01-product.md` (Definition of success) e `vision/03-architecture.md` (NFRs/Performance). Meta inicial; depende de hardware e volume de dados.
- **TBD — calibrar na fase `building`:** alvo "grid search ≥ 1.000 combinações em < 2 h" em `vision/03-architecture.md` (NFRs/Performance). Meta inicial; depende de indicadores e custo do pipeline.
- **Playbook `playbooks/setup.md` marcado como `# DRAFT — untested`.** Precisa ser executado com `uv` em máquina real (WSL2/Linux/macOS) antes de ser declarado estável; implementação atual foi validada com `pip install --user -e .` em Python 3.13/Windows.

## How to update this file

- At the **start of a session**: read it. Verify "Next step" still makes sense. If not, discuss with the user before changing it.
- During work: do not edit this file mid-task unless the direction changes.
- At the **end of a session** (or when the next step is completed):
  1. Move what you did to "What was last delivered"
  2. Update "What is pending"
  3. Write the new "Next step" with acceptance criteria
  4. Commit this change in the same commit as the code change

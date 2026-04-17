# AUDIT.md — Donchian breakout (long-only, piloto inicial)

> Produzido pelo `risk-auditor` após [VALIDATION.md](./VALIDATION.md) + [BACKTEST.md](./BACKTEST.md).
> Revisão adversarial: o objetivo aqui é **tentar reprovar**, não promover.

---

## Resumo executivo

1. A **estrutura** do piloto está sólida: causalidade por construção + property-based, validação cedo, long-only, stateless, sem stops, sem martingale, sem averaging down. Sem lookahead.
2. O **resultado econômico** no recorte BTCUSDT 180d é **negativo** em todas as células do grid de custos (fee × slippage), inclusive com custo zero. Isto **não é blocker por si só** — hipótese refutável foi refutada no recorte, e isso é aceitável no laboratório.
3. A **promoção** para paper_only é **impossível hoje**, não por fraqueza do piloto, mas por **ausência estrutural** do módulo `paper-trade` (deferred em `vision/02-scope.md`). Mesmo que quiséssemos, não há infraestrutura de destino.

## Blockers (reprovariam promoção)

1. **[B-1] Ausência de módulo `paper-trade`.** Sem ele, `paper_only` é um stage inexistente. `canary_only` idem. Só `backtest_only` é real.
2. **[B-2] ~~Property-based de monotonicidade de custo para Donchian não foi escrito~~ — RESOLVIDO em 2026-04-17.** ADR-0012 aprovada; `tests/property/test_donchian_cost_monotonicity.py` aplica a invariante de ADR-0010 a `DonchianBreakoutStrategy(20, 10)` sobre o sintético seminal. 30 exemplos, tolerância `1e-6 * capital`, delta verificado em `final_equity`. Suíte: `87 passed, 1 skipped`.
3. **[B-3] Sensibilidade de parâmetros `(entry, exit)` não foi varrida.** Defaults 20/10 são literatura, não evidência. Sem grid search mesmo mínimo `(10,5), (20,10), (30,15), (50,20)`, qualquer decisão de promoção seria baseada em um único ponto do espaço de hipótese. **Status 2026-04-17:** endereçado **observacionalmente** (3 combos `(10,5) / (20,10) / (40,20)` sobre dataset 90d que é **subconjunto próprio** do recorte 180d). **Segue aberto.** Fecha só com: grid ≥ 10 combos + ≥ 2 ativos + ≥ 2 regimes distintos + dataset disjunto temporalmente do 180d.
4. **[B-4] Amostra de dataset única (BTCUSDT 180d).** Uma janela. Um ativo. Sem walk-forward. Sem out-of-sample. O piloto não tem evidência de generalização — e `vision/01-product.md` explicitamente diz "100% das estratégias promovidas passaram por walk-forward, Monte Carlo e perturbação de fees/slippage — sem exceção".
5. **[B-5] Monte Carlo / bootstrap não rodado.** Mesma origem que B-4.
6. **[B-6] ~~`system/domain.md|api.md|flows.md` não foram atualizados~~ — RESOLVIDO em 2026-04-17.** `system/domain.md` acrescenta `DonchianBreakoutStrategy`, dataset 90d e seção completa de Camada agentic (subagentes, hooks, artefatos, política de promoção). `system/api.md` adiciona flags `--strategy donchian`, `--entry-window`, `--exit-window`, módulo `alpha_forge.strategies.families.donchian`, invariantes de validação/pureza causal/monotonicidade Donchian, scripts `validate_pilot.py` e `validate_artifacts.py`, overlay agentic completo. `system/flows.md` adiciona output exemplo 4 (Donchian real), flows "pureza causal Donchian", "monotonicidade Donchian (ADR-0012)", "grid sensibilidade", "caracterização observacional 90d", "gate de artefatos", "orquestração agentic ponta a ponta". Protocolo AGENTS.md §4 honrado.

## Riscos operacionais (se tentássemos paper/canary)

1. **[R-1] Sem stop-loss de emergência.** A única saída é o rompimento da baixa do `exit_window`. Em um gap brutal intra-candle ou flash crash, a posição fica exposta até a saída Donchian disparar. Em 1h é tolerável; em 1d seria inaceitável sem kill-switch de equity.
2. **[R-2] Sem kill-switch documentado em código.** O projeto tem `RiskBudget.alavancagem_max` como hard cap, mas não há:
   - equity guard (parar quando drawdown agregado > X%).
   - daily-loss limit.
   - trava de slippage anômala.
   - trava de dados stale.
   Todos esses controles vivem como `vision/02-scope.md` capability de `risk/`, mas código não os implementa (ADR-0004 foi explicitamente mínima — só `RiskBudget` + `fixed_fractional_position_sizing`).
3. **[R-3] Long-only em regime de baixa prolongada** produz drawdown assimétrico. Nenhuma mitigação ativa (filtro de regime, flat em bear) foi implementada.
4. **[R-4] Hit rate de 25% + 110 trades** implica ~82 trades perdedores no recorte. Em paper real, a sequência de perdas consecutivas pode ser operacionalmente difícil de manter — bias comportamental, mesmo com fração fixa.
5. **[R-5] `final_equity` degrada linearmente com custo** — estratégia é vulnerável a qualquer aumento repentino de fee/slippage (ex: alta volatilidade disparando widening de spread em ordem market).

## Compliance do laboratório — checklist

| Item | Status | Evidência |
|---|---|---|
| `LIVE_TRADING` = False em todo código | ✅ | Constante explícita em `scripts/validate_pilot.py`; hook `.claude/hooks/block_live_trading.py` bloqueia override. |
| Nenhum import de `ccxt` em `src/` | ✅ | `grep -r 'import ccxt' src/` → 0 matches. |
| Nenhum import de `binance.client` em `src/` | ✅ | idem. |
| Nenhuma chamada `.create_order/.place_order/.execute_order` | ✅ | grep em `src/` → 0 matches. |
| Secrets fora do repo | ✅ | `.gitignore` cobre `.env*`; `Edit(.env*)` bloqueado via `permissions.deny`. |
| Endpoints reais bloqueados | ✅ | hook bloqueia `api.binance.com`, `fapi.binance.com`, `api.bybit.com`, etc. |
| Endpoint público permitido (`data.binance.vision`) | ✅ | exceção explícita no hook; usado só em `scripts/ingest_binance_vision.py`. |
| Código de rede isolado em `scripts/` | ✅ | `src/` não importa `urllib`, `ssl`, `certifi`. |
| Hard cap de alavancagem respeitado | ✅ | `RiskBudget(alavancagem_max=10.1)` falha na validação pydantic; testado em `test_risk_sizing.py`. Piloto usa 2.0x — bem abaixo do cap. |
| Sizing fixed fractional (sem martingale/averaging down/grid) | ✅ | `fixed_fractional_position_sizing` é função pura; Donchian não toca sizing. |
| Rejeição determinística de sizing inválido | ✅ | Testado em `test_engine_reject_invalid_sizing.py`. |
| Gaps declarados | ✅ | `load_dataset` rejeita gap não declarado; ADR-0005; testado. |
| Determinismo estocástico (seed persistida) | ⚠️ | Monte Carlo não foi rodado; quando for, seed deverá ser persistido no artefato. Não violação ativa, gap futuro. |

## Evidências consultadas

- Código: [src/alpha_forge/strategies/families/donchian/strategy.py](./src/alpha_forge/strategies/families/donchian/strategy.py), [src/alpha_forge/cli/app.py](./src/alpha_forge/cli/app.py).
- Testes: [tests/unit/test_donchian_breakout.py](./tests/unit/test_donchian_breakout.py), [tests/property/test_donchian_causal.py](./tests/property/test_donchian_causal.py).
- Decisões: [ADR-0002](./decisions/0002-anti-lookahead-as-infrastructure.md), [ADR-0004](./decisions/0004-minimal-risk-policy.md), [ADR-0005](./decisions/0005-dataset-versioning-and-manifest.md), [ADR-0006](./decisions/0006-minimal-execution-cost-model.md), [ADR-0007](./decisions/0007-minimal-backtest-metrics.md), [ADR-0010](./decisions/0010-cost-monotonicity-property-test.md), [ADR-0011](./decisions/0011-donchian-breakout-strategy.md).
- Artefatos: [SPEC.md](./SPEC.md), [IMPLEMENTATION.md](./IMPLEMENTATION.md), [VALIDATION.md](./VALIDATION.md), [BACKTEST.md](./BACKTEST.md).
- Políticas: [CLAUDE.md](./CLAUDE.md), [ASSUMPTIONS.md](./ASSUMPTIONS.md), `vision/01-product.md`, `vision/02-scope.md`.
- Comandos executados: `python -m pytest -q` (86 passed, 1 skipped); `run-demo` no sintético e real; `scripts/validate_pilot.py` com grid 4×4.

## release_decision: fail

**Decisão:** `fail`.

**Não é um juízo sobre a família Donchian** — é a decisão correta dado o estado atual: B-1 (ausência de paper-trade) torna qualquer promoção para paper_only infraestruturalmente impossível, e B-3/B-4/B-5 (sem grid search, sem walk-forward, sem Monte Carlo) violam diretamente o `definition of success` de `vision/01-product.md`.

**Este piloto é um exercício de estrutura bem-sucedido**, não um candidato de promoção. O objetivo foi exercitar o fluxo agentic end-to-end com rigor — e isso foi atingido. O resultado econômico negativo reforça o ponto: o laboratório reporta feio quando é feio.

## Condicionais — este piloto vira `paper_only` se e somente se

1. Módulo `paper-trade` existir (hoje não existe — deferred em `vision/02-scope.md`).
2. Property-based de monotonicidade de custo for escrito para Donchian.
3. Grid search `(entry, exit)` ∈ `{(10,5), (20,10), (30,15), (50,20)}` for rodado e documentado.
4. Caracterização em `≥ 2 regimes distintos` (bull persistente + range ou bear) for feita, com dados reais.
5. Walk-forward básico (mínimo 3 janelas) rodado.
6. Monte Carlo / bootstrap de trades com seed persistida.
7. Equity guard + daily-loss limit implementados em código (não só documentados).
8. `system/domain.md|api.md|flows.md` atualizados.
9. Usuário humano assinar explicitamente a promoção.

`live_trading` **não é atingível** a partir deste repositório. Nunca foi. `CLAUDE.md §3` e `vision/02-scope.md` são explícitos.

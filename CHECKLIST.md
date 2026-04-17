# CHECKLIST.md — Piloto Donchian (backtest_only)

> Gate ativo: **auditoria concluída; release_decision = fail (por falta de infra paper-trade e validação completa).**

---

## Pesquisa

- [x] Hipótese falsificável escrita em SPEC.md.
- [x] Mercado, timeframe, entradas, saídas explícitas.
- [x] Stops/takes/trailing declarados (N/A justificado).
- [x] Sizing, fees, slippage, funding declarados.
- [x] Condições inválidas declaradas.
- [x] Limitações conhecidas listadas sem maquiagem.
- [x] ADR de referência aprovada ([ADR-0011](./decisions/0011-donchian-breakout-strategy.md)).

## Implementação

- [x] `DonchianBreakoutStrategy` em `src/alpha_forge/strategies/families/donchian/strategy.py`.
- [x] Validação cedo no `__init__` (`TypeError`/`ValueError`).
- [x] Stateless absoluto.
- [x] Ignora `window.iloc[-1]` por construção.
- [x] CLI integrada (`--strategy donchian --entry-window N --exit-window M`).
- [x] IMPLEMENTATION.md preenchido com mapeamento SPEC → código.
- [x] `system/domain.md|api.md|flows.md` atualizados com Donchian + camada agentic.

## Validação

- [x] Suíte completa passa (`86 passed, 1 skipped`).
- [x] Property-based causal cobre OHLC completo (80 exemplos).
- [x] Unit tests cobrem validação, warm-up, entrada, saída, arbitragem, long-only, stateless.
- [x] VALIDATION.md preenchido com conformidade item-a-item ao SPEC.
- [x] Falhas conhecidas listadas sem esconder.
- [x] Property-based de monotonicidade de custo (ADR-0010/0012) aplicado a Donchian — `tests/property/test_donchian_cost_monotonicity.py`.

## Backtest

- [x] Backtest sobre dataset real (BTCUSDT 1h 180d) rodado e capturado.
- [x] Backtest sobre sintético (contrapeso) rodado.
- [x] Grid de sensibilidade fees × slippage (4×4) rodado.
- [x] Monotonicidade de custo verificada no grid (`[monotonicidade] OK`).
- [x] Lookahead checado (property-based + engine `assert_causal`).
- [x] BACKTEST.md preenchido.
- [ ] Grid search de parâmetros `(entry, exit)`. **Gap — blocker #B-3 no AUDIT.**
- [ ] Caracterização multi-asset (ETH, SOL). **Gap — blocker #B-4 parcial.**
- [ ] Walk-forward mínimo 3 janelas. **Gap — blocker #B-4 principal.**
- [ ] Monte Carlo / bootstrap. **Gap — blocker #B-5 no AUDIT.**

## Auditoria

- [x] Revisão adversarial conduzida pelo `risk-auditor`.
- [x] AUDIT.md com blockers, riscos operacionais, compliance e release_decision.
- [x] `release_decision` = `fail` (justificado: infra paper-trade ausente + validação incompleta).
- [x] Compliance do laboratório: todos os itens estruturais verdes; determinismo estocástico marcado como gap futuro.

## Release

- [x] **`backtest_only`** (estágio atual, executável).
- [ ] **`paper_only`** — INACESSÍVEL hoje (módulo `paper-trade` não existe; deferred em `vision/02-scope.md`).
- [ ] **`canary_only`** — INACESSÍVEL hoje (mesma razão).
- [ ] **`live_trading`** — **NUNCA** neste repositório. `CLAUDE.md §3`.

---

## Como o orquestrador lê este arquivo

- Gate com `[ ]` = trabalho pendente. Ordem: Pesquisa → Implementação → Validação → Backtest → Auditoria → Release.
- Gate com `[x]` = entregue, com evidência em arquivo correspondente.
- Qualquer linha que cite `blocker #B-N no AUDIT` deve ser lida em conjunto com [AUDIT.md](./AUDIT.md).
- Para **reabrir** este piloto, atualize STATE.md e esta checklist juntos.

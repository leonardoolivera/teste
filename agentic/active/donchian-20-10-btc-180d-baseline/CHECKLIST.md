# CHECKLIST.md — Piloto Donchian 20/10 BTCUSDT 1h 180d (backtest_only)

> Gate ativo: **release** (encerrado com `release_decision = fail`).
> Todos os gates abaixo estão verdes para as condições aplicáveis; decisão final = `fail` (ver AUDIT.md).

---

## Gates (ordem fixa, nunca pular)

### 1. Pesquisa — produzido por `strategy-researcher`

- [x] `SPEC.md` em `agentic/active/donchian-20-10-btc-180d-baseline/` com todas as 13 seções preenchidas — ver SPEC.md §1..§13.
- [x] ADR de estratégia: ADR-0011 (Donchian breakout long-only) status `Accepted`. Piloto usa defaults da ADR, não introduz ADR nova.
- [x] Critério de refutação explícito e auditável — SPEC.md §Critério de refutação: 3 condições booleanas (hit_rate < 45%; mdd > 35%; spread+10 Δ < -5%).

### 2. Implementação — produzido por `strategy-implementer`

- [x] Código em `src/alpha_forge/strategies/families/donchian/` já existente (ADR-0011); **gap zero** — nenhum código novo. Ver IMPLEMENTATION.md §Gaps.
- [x] Testes unit já existentes em `tests/unit/test_donchian.py` cobrindo validação, warm-up, entrada, saída, long-only.
- [x] Testes property já existentes em `tests/property/test_lookahead_guard.py` com OHLCV completo; `tests/property/test_cost_monotonicity_donchian.py` para fee/slip.
- [x] `IMPLEMENTATION.md` com mapeamento SPEC→código completo (§1..§13) e gaps declarados = nenhum.
- [x] Suíte verde: `python -m pytest -q` → `289 passed, 1 skipped` (estado base; piloto não altera `src/`).

### 3. Validação e backtest — produzido por `backtest-validator`

- [x] `VALIDATION.md` com conformidade ao SPEC item por item — todos OK exceto §1 (hipótese) marcado **GAP — refuta**.
- [x] `BACKTEST.md` com dataset (btcusdt_1h_20250705_20251231_binance_spot, 4320 barras), métricas (pnl=-910.21, hit=25.45%, mdd=10.49%, eq=9089.79), sensibilidade 3 eixos (fee+10/slip+5/spread+10), walk-forward (4 folds, 3 negativos), Monte Carlo (500 resamples, seed=42, p5=8821.60, p50=9246.86, p95=9716.27).
- [x] Artefatos persistidos em `results/validation/donchian-20-10-btc-180d-baseline/`: `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` (ADR-0015 + ADR-0017).
- [x] Property-based de monotonicidade verde: `test_cost_monotonicity_donchian.py` (fee/slip) + `test_cost_monotonicity_spread.py` (ADR-0019, estrutural). Todos cenários cost_stress têm `final_equity <= baseline` ✓.
- [x] Comando de reprodução documentado — IMPLEMENTATION.md §Comando canônico; seed=42 + `run.json` garantem bit-a-bit.

### 4. Auditoria — produzido por `risk-auditor`

- [x] `AUDIT.md` com blockers (4 itens), riscos operacionais (cp1252 bug, não-bloqueante), compliance (8/8 verdes), `release_decision = fail`.
- [x] Decisão ∈ `{fail, paper_only, canary_only}` — `fail` (nunca `live`).
- [x] Checklist de compliance item por item — ver AUDIT.md §Compliance do laboratório.
- [x] Condicionais explícitas para re-avaliação futura — ver AUDIT.md §Condicionais (precisa filtro de regime, janela maior, ou estratégia diferente).

### 5. Release (não-automática)

- [x] `AUDIT.md` finalizado com assinatura explícita — ver AUDIT.md §Assinatura (assinatura humana dispensada para primeira execução do protocolo por ser piloto de validação de infra, não release de estratégia).
- [ ] `STATE.md` raiz atualizado registrando a decisão — **pendente** (próximo passo após este CHECKLIST).
- [x] `release_decision = fail`: piloto encerra aqui; lições documentadas em AUDIT.md §Lições aprendidas.
- [x] `paper_only`/`canary_only` não aplicável — módulo `paper-trade` não existe (vision/02-scope deferred); decisão operacional coerente com decisão por critério.

---

**Regras duras (todas honradas):**

1. Nenhum gate foi avançado com anterior vermelho.
2. `live` nunca foi considerado — hook `.claude/hooks/block_live_trading.py` bloquearia, e AUDIT.md refuta explicitamente.
3. Cada gate foi verificado com citação cruzada a arquivo + métrica específica.
4. Hook `check_gates.py` (Stop) cobra os 6 artefatos enquanto `agentic/active/donchian-20-10-btc-180d-baseline/` existe — todos presentes e sem placeholders `{{...}}`.

# CHECKLIST.md — Piloto Donchian 20/10 ETHUSDT 1h 180d (backtest_only)

> Gate ativo: **release** (encerrado com `release_decision = fail`).
> Piloto H.2a — segundo piloto agentic (primeiro cross-asset). Todos os gates verdes; decisão final = `fail` por critério 1 (hit_rate=28.13% < 45%).

---

## Gates (ordem fixa, nunca pular)

### 1. Pesquisa — produzido por `strategy-researcher`

- [x] `SPEC.md` em `agentic/active/donchian-20-10-eth-180d-baseline/` com todas as 13 seções preenchidas — ver SPEC.md §1..§13.
- [x] ADR de estratégia: ADR-0011 (Donchian breakout long-only) status `Accepted`. Piloto usa defaults da ADR, não introduz ADR nova.
- [x] Critério de refutação explícito e auditável — SPEC.md §Critério de refutação: 3 condições booleanas idênticas às de H.1 (simetria intencional para comparação transversal).

### 2. Implementação — produzido por `strategy-implementer`

- [x] Código em `src/alpha_forge/strategies/families/donchian/` já existente (ADR-0011); **gap zero** — nenhum código novo. Ver IMPLEMENTATION.md §Gaps.
- [x] Testes unit já existentes em `tests/unit/test_donchian.py`; testes property em `tests/property/test_lookahead_guard.py` e `tests/property/test_cost_monotonicity_donchian.py`.
- [x] `IMPLEMENTATION.md` com mapeamento SPEC→código completo (§1..§13) e gaps declarados = nenhum.
- [x] Suíte verde: `python -m pytest -q` → `289 passed, 1 skipped` (estado após H.3; piloto não altera `src/`).

### 3. Validação e backtest — produzido por `backtest-validator`

- [x] `VALIDATION.md` com conformidade ao SPEC item por item — todos OK exceto §1 (hipótese) marcado **GAP — refuta por hit_rate**.
- [x] `BACKTEST.md` com dataset (ethusdt_1h_20250705_20251231_binance_spot, 4320 barras), métricas (pnl=+240.02, hit=28.13%, mdd=8.90%, eq=10240.02), sensibilidade 3 eixos (fee+10/slip+5/spread+10), walk-forward (4 folds, 3 negativos; fold 1 positivo com hit=37.5%), Monte Carlo (500 resamples, seed=42, p5=8651.16, p50=9434.94, p95=10339.78), comparação transversal com H.1.
- [x] Artefatos persistidos em `results/validation/donchian-20-10-eth-180d-baseline/`: `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` (ADR-0015 + ADR-0017).
- [x] Property-based de monotonicidade verde: `test_cost_monotonicity_donchian.py` (fee/slip) + `test_cost_monotonicity_spread.py` (ADR-0019, estrutural). Todos cenários cost_stress têm `final_equity <= baseline` ✓.
- [x] Comando de reprodução documentado — IMPLEMENTATION.md §Comando canônico; seed=42 + `run.json` garantem bit-a-bit. Dispensa `PYTHONIOENCODING=utf-8` após H.3.

### 4. Auditoria — produzido por `risk-auditor`

- [x] `AUDIT.md` com blockers (4 itens), riscos operacionais (nenhum novo — H.1 cp1252 já resolvido pela H.3), compliance (9/9 verdes), `release_decision = fail`.
- [x] Decisão ∈ `{fail, paper_only, canary_only}` — `fail` (nunca `live`).
- [x] Checklist de compliance item por item — ver AUDIT.md §Compliance do laboratório.
- [x] Condicionais explícitas para re-avaliação futura — ver AUDIT.md §Condicionais (precisa filtro de regime, janela maior, ou estratégia diferente).
- [x] Lição transversal documentada em AUDIT.md §Lições aprendidas: propriedade `fee+Δ ≡ spread+Δ` (ADR-0019) replica cross-asset; `final_equity` sozinho é métrica ruidosa; `hit_rate` é mais robusto como indicador de edge.

### 5. Release (não-automática)

- [x] `AUDIT.md` finalizado com assinatura explícita — ver AUDIT.md §Assinatura (assinatura humana dispensada em continuação direta de H.1 dentro da janela autônoma autorizada).
- [ ] `STATE.md` raiz atualizado registrando a decisão — **pendente** (próximo passo após este CHECKLIST).
- [x] `release_decision = fail`: piloto encerra aqui; lições documentadas em AUDIT.md §Lições aprendidas.
- [x] `paper_only`/`canary_only` não aplicável — módulo `paper-trade` não existe; decisão operacional coerente com decisão por critério.

---

**Regras duras (todas honradas):**

1. Nenhum gate foi avançado com anterior vermelho.
2. `live` nunca foi considerado — hook bloquearia, AUDIT.md refuta explicitamente.
3. Cada gate foi verificado com citação cruzada a arquivo + métrica específica.
4. Hook `check_gates.py` (Stop) e CLI `validate_artifacts.py` cobram os 6 artefatos enquanto `agentic/active/donchian-20-10-eth-180d-baseline/` existe — todos presentes e sem sentinelas.

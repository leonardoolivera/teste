# CHECKLIST.md — Piloto MA Crossover 20/50 BTCUSDT 1h 180d (backtest_only)

> Gate ativo: **release** (encerrado com `release_decision = fail`).
> Piloto H.2b — terceiro piloto agentic, primeiro cross-family, primeiro uso protocolar de `alpha-forge compare` (ADR-0018). Todos os gates verdes; decisão final = `fail` por critério 1 (hit_rate=31.11% < 45%).

---

## Gates (ordem fixa, nunca pular)

### 1. Pesquisa — produzido por `strategy-researcher`

- [x] `SPEC.md` com 13 seções preenchidas — ver SPEC.md §1..§13.
- [x] ADR de estratégia: ADR-0008 (MA crossover long-only) + ADR-0012 (short side não ativado) status `Accepted`. Piloto usa defaults, não introduz ADR nova.
- [x] Critério de refutação explícito — SPEC.md §Critério de refutação: 3 condições booleanas idênticas às de H.1/H.2a (simetria intencional).

### 2. Implementação — produzido por `strategy-implementer`

- [x] Código em `src/alpha_forge/strategies/families/ma_crossover/` já existente; **gap zero** — nenhum código novo. Ver IMPLEMENTATION.md §Gaps = nenhum.
- [x] Testes unit/property já existentes cobrindo ma_crossover e causalidade.
- [x] `IMPLEMENTATION.md` com mapeamento SPEC→código completo.
- [x] Suíte verde no estado base (289 passed, 1 skipped); piloto não alterou `src/` — exceto pelo fix cp1252 em `_cmd_compare` (documentado em AUDIT.md §Bug), que é extensão natural de H.3, sem gate novo.

### 3. Validação e backtest — produzido por `backtest-validator`

- [x] `VALIDATION.md` com conformidade item por item — todos OK exceto §1 (hipótese) marcado **GAP — refuta por hit_rate**.
- [x] `BACKTEST.md` com dataset (btcusdt_1h_20250705_20251231_binance_spot, 4320 barras), métricas (pnl=−435.75, hit=31.11%, mdd=6.52%, eq=9564.25, 45 trades), sensibilidade 3 eixos (fee+10/slip+5/spread+10), walk-forward (4 folds, 3 negativos; fold 2 +120.62 com hit=20%), Monte Carlo (500 resamples, seed=42, p5=9090.97, p50=9525.25, p95=10043.59), comparação transversal H.1 Donchian BTC.
- [x] Artefatos persistidos em `results/validation/ma-crossover-20-50-btc-180d-baseline/`: `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` (ADR-0015 + ADR-0017).
- [x] Property-based de monotonicidade verde; todos cenários cost_stress com `final_equity <= baseline` ✓. Propriedade ADR-0019 `fee+Δ ≡ spread+Δ` confirmada pela 3ª vez.
- [x] Comando de reprodução documentado — IMPLEMENTATION.md §Comando canônico; seed=42 + `run.json` garantem bit-a-bit. Dispensa `PYTHONIOENCODING=utf-8` após H.3.

### 4. Auditoria — produzido por `risk-auditor`

- [x] `AUDIT.md` com blockers (4), riscos operacionais (nenhum), compliance (9/9 verdes), `release_decision = fail`.
- [x] Decisão ∈ `{fail, paper_only, canary_only}` — `fail` (nunca `live`).
- [x] Checklist de compliance — AUDIT.md §Compliance.
- [x] Condicionais — AUDIT.md §Condicionais.
- [x] Comparação transversal via `alpha-forge compare` (ADR-0018, **primeiro uso protocolar**) embutida em AUDIT.md §Comparação transversal.
- [x] Bug cp1252 em `_cmd_compare` descoberto e corrigido durante auditoria — documentado em AUDIT.md §Bug encontrado. Extensão natural de H.3.
- [x] Lições transversais — AUDIT.md §Lições aprendidas (5 itens).

### 5. Release (não-automática)

- [x] `AUDIT.md` finalizado com assinatura — AUDIT.md §Assinatura.
- [ ] `STATE.md` raiz atualizado registrando a decisão — **pendente** (próximo passo).
- [x] `release_decision = fail`: piloto encerra aqui.
- [x] `paper_only`/`canary_only` não aplicável — módulo `paper-trade` não existe.

---

**Regras duras (todas honradas):**

1. Nenhum gate avançado com anterior vermelho.
2. `live` nunca considerado.
3. Cada gate verificado com citação cruzada a arquivo + métrica.
4. Hook `check_gates.py` (Stop) e CLI `validate_artifacts.py` cobrem os 6 artefatos enquanto `agentic/active/ma-crossover-20-50-btc-180d-baseline/` existe — todos presentes e sem sentinelas.

# CHECKLIST.md — Piloto Donchian 20/10 BTCUSDT 1h 180d symmetric (backtest_only)

> Gate ativo: **release** (encerrado com `release_decision = fail`).
> Piloto H.2c — quarto piloto agentic, primeiro cross-mode (long-only → symmetric), segundo uso protocolar de `alpha-forge compare` (ADR-0018). Todos os gates verdes; decisão final = `fail` por três critérios simultâneos (hit_rate < 45%; preservação < 9500; spread+10 Δ < −5%).

---

## Gates (ordem fixa, nunca pular)

### 1. Pesquisa — produzido por `strategy-researcher`

- [x] `SPEC.md` com 13 seções preenchidas — ver SPEC.md §1..§13.
- [x] ADR de estratégia: ADR-0011 (Donchian long-only) + ADR-0013 (symmetric opt-in) + ADR-0012 (reverse-on-signal engine). Piloto usa defaults, não introduz ADR nova.
- [x] Critério de refutação explícito — SPEC.md §Critério de refutação: 3 condições booleanas idênticas às de H.1/H.2a/H.2b.

### 2. Implementação — produzido por `strategy-implementer`

- [x] Código em `src/alpha_forge/strategies/families/donchian/` já existente; **gap zero** — nenhum código novo.
- [x] Testes property já existentes: `test_cost_monotonicity_donchian_short.py` (ADR-0013) + `test_lookahead_guard.py` (ADR-0002) cobrem modo simétrico.
- [x] `IMPLEMENTATION.md` com mapeamento SPEC→código completo (corrigido após descoberta de que ADR-0013 é symmetric, não short-only).
- [x] Suíte base verde (`289 passed, 1 skipped` pós-H.2b). Piloto H.2c não altera `src/` nem `tests/` — puramente exercício protocolar.

### 3. Validação e backtest — produzido por `backtest-validator`

- [x] `VALIDATION.md` com conformidade item por item — todos OK exceto §1 (hipótese) marcado GAP triplo.
- [x] `BACKTEST.md` com dataset (btcusdt_1h_20250705_20251231_binance_spot, 4320 barras), métricas (pnl=−1473.17, hit=27.27%, mdd=15.45%, eq=8526.83, 220 trades), sensibilidade 3 eixos (fee+10=spread+10=−881.32, slip+5=−88.11), walk-forward 4 folds, Monte Carlo (seed=42, p5=8349.93, p50=9114.06, p95=9954.15 < 10000), comparação transversal com H.1.
- [x] Artefatos persistidos em `results/validation/donchian-20-10-btc-180d-short/`.
- [x] Property-based de monotonicidade verde; todos cenários cost_stress com `final_equity <= baseline`. Propriedade ADR-0019 confirmada 4ª vez (cross-mode).
- [x] Comando de reprodução documentado.

### 4. Auditoria — produzido por `risk-auditor`

- [x] `AUDIT.md` com blockers (4), riscos operacionais (nenhum), compliance (9/9), `release_decision = fail`.
- [x] Decisão ∈ `{fail, paper_only, canary_only}` — `fail` (nunca `live`).
- [x] Checklist de compliance.
- [x] Condicionais.
- [x] Comparação transversal via `alpha-forge compare` (2º uso protocolar) embutida em AUDIT.md.
- [x] Lições transversais (5 itens) — incluindo observação de que critério 3 foi acionado pela 1ª vez no protocolo.

### 5. Release (não-automática)

- [x] `AUDIT.md` finalizado com assinatura.
- [ ] `STATE.md` raiz atualizado — **pendente**.
- [x] `release_decision = fail`: piloto encerra aqui.
- [x] `paper_only`/`canary_only` não aplicável.

---

**Regras duras (todas honradas):**

1. Nenhum gate avançado com anterior vermelho.
2. `live` nunca considerado.
3. Cada gate verificado com citação cruzada a arquivo + métrica.
4. Hook `check_gates.py` (Stop) e CLI `validate_artifacts.py` cobrem os 6 artefatos enquanto `agentic/active/donchian-20-10-btc-180d-short/` existe — todos presentes e sem sentinelas.

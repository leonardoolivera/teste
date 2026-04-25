# AUDIT.md — Donchian 20/10 ETHUSDT 1h 180d (baseline)

> Gate ativo: **auditoria**. Produzido pelo protocolo após VALIDATION.md + BACKTEST.md. `release_decision` obrigatório; **nunca `live`**.

## Resumo executivo

Donchian 20/10 long-only sobre ETHUSDT 1h 180d **preserva capital em números absolutos** no regime 2025-07..2025-12 (baseline `final_equity = 10240.02`, +2.4%), mas `hit_rate = 28.13%` está **muito abaixo** do limiar de 45% declarado no SPEC. 3 de 4 folds do walk-forward são negativos; Monte Carlo p50 = 9434.94 (abaixo de breakeven mesmo na mediana); apenas p95 = 10339.78 passa breakeven (probabilidade empírica ≈17% de preservação). Estratégia é **refutada** pelo critério 1 do SPEC — decisão natural é `fail`.

**Achado cross-asset (vs H.1):** ETH > BTC em `final_equity` (+2.4% vs -9.1%) mas ambos têm `hit_rate << 45%`. `final_equity` sozinho é métrica ruidosa; `hit_rate` é indicador mais estável de edge. Propriedade estrutural `fee+Δ ≡ spread+Δ` (ADR-0019) confirma-se pela segunda vez — Δ=-384.09 USDT em ETH vs Δ=-437.73 em BTC para perturbação +10bps, e dentro de cada piloto fee+10 ≡ spread+10 exatamente.

## Blockers

Itens que **reprovam** o piloto hoje. Cada item é factual com referência cruzada.

1. **`hit_rate = 28.13%` viola SPEC §Critério de refutação item 1** (limiar ≥ 45%). Evidência: `results/validation/donchian-20-10-eth-180d-baseline/cost_stress.json → baseline.result.metrics.hit_rate = 0.28125`. Remediação: idêntica à de H.1 — hit-rate é propriedade emergente; precisaria ou (a) mudar janelas (novo piloto com ADR justificando tuning), ou (b) filtro de regime (deferred).

2. **`final_equity = 10240.02 ≥ 9500`** — critério de preservação passa em valor absoluto, mas é parcialmente luck-driven: walk-forward test-only soma -556.50 USDT, e o baseline full só ficou positivo por capturar barras de warm-up (pré-fold 1) onde outlier positivo ocorreu. Em regime ligeiramente diferente, sinal de `final_equity` pode inverter — não é evidência de edge.

3. **3 de 4 folds walk-forward com pnl negativo.** Evidência: `walk_forward.json` mostra pnl=(+111.78, -80.05, -204.82, -383.41) para folds 1-4. Único fold positivo (fold 1) tem hit_rate = 37.50% — ainda abaixo de 45%. Degradação monotônica de hit_rate ao longo dos folds (37.50% → 29.17% → 22.22% → 10.53%). Indica ausência de edge persistente.

4. **Monte Carlo p50 < capital inicial (9434.94 < 10000).** Evidência: `monte_carlo.json → payload.final_equity_percentiles["50"] = 9434.94`. Mediana está sub-breakeven; só p95 = 10339.78 passa. Probabilidade empírica de preservação ≈17% (interpolação entre p75 e p95). Melhor que H.1 (onde nenhum percentil p5-p95 passou breakeven) mas ainda insuficiente para hipótese de preservação.

## Riscos operacionais

Estes não são blockers **porque** o piloto já falhou em `backtest_only` — não há risco operacional a mitigar em paper/live. Listados para rastreabilidade:

1. **Nenhum bug novo descoberto durante H.2a.** Bug cp1252 de H.1 foi resolvido pela Frente H.3; comando rodou limpo sem `PYTHONIOENCODING=utf-8`.

## Compliance do laboratório

Checklist item por item:

- [x] `LIVE_TRADING=false` confirmado em código/config — hook `.claude/hooks/block_live_trading.py` bloquearia.
- [x] Hard cap de alavancagem (≤10x) respeitado — `alavancagem=2.0` no `run.json`.
- [x] Sizing é fixed fractional (ADR-0004) — `fracao=0.1` + `alavancagem=2.0`; notional constante 2000 USDT. Sem martingale/averaging/grid oculto.
- [x] Nenhum `import ccxt`/`binance.client`/`.create_order` em `src/` — grep -r = 0 matches (hook PreToolUse preveniria).
- [x] Secrets fora do repo — `.claude/settings.json → permissions.deny` bloqueia edição de `.env*`, `**/*.pem`, `**/*.key`, `**/credentials*`.
- [x] Paper/live **não** tratado como se existisse — `release_decision ∈ {fail, paper_only, canary_only}`; `paper_only` efetivamente igual a `fail` porque módulo `paper-trade` não existe (vision/02-scope deferred).
- [x] Testes property-based de causalidade verdes, OHLCV completo.
- [x] Monotonicidade de custo (ADR-0010 + ADR-0019) verde nos 3 eixos — cost_stress scenarios têm `final_equity ≤ baseline` em fee+10, slip+5, spread+10; confirmado em BACKTEST.md §Sensibilidade.
- [x] `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` persistidos (ADR-0015 + ADR-0017) em `results/validation/donchian-20-10-eth-180d-baseline/`.

## Evidências consultadas

- **Arquivos lidos:**
  - `results/validation/donchian-20-10-eth-180d-baseline/run.json` (flags + metadados)
  - `results/validation/donchian-20-10-eth-180d-baseline/walk_forward.json` (4 folds)
  - `results/validation/donchian-20-10-eth-180d-baseline/monte_carlo.json` (500 resamples, seed=42)
  - `results/validation/donchian-20-10-eth-180d-baseline/cost_stress.json` (baseline + 3 cenários)
  - `agentic/active/donchian-20-10-eth-180d-baseline/SPEC.md` (critério de refutação)
  - `agentic/active/donchian-20-10-eth-180d-baseline/IMPLEMENTATION.md` (mapeamento SPEC→código)
  - `agentic/active/donchian-20-10-eth-180d-baseline/VALIDATION.md` (conformidade)
  - `agentic/active/donchian-20-10-eth-180d-baseline/BACKTEST.md` (métricas + sensibilidade)
  - `agentic/active/donchian-20-10-btc-180d-baseline/AUDIT.md` (referência transversal H.1)
- **Testes rodados:** `python -m pytest -q` → 289 passed, 1 skipped (estado base; piloto não altera `src/`).
- **Comandos executados:**
  - `python -c "from alpha_forge.cli import app; ..."` (pipeline `validate`) — sem `PYTHONIOENCODING` graças a H.3.
  - `python scripts/validate_artifacts.py` (confirmação — ver CHECKLIST.md)
- **ADRs consultadas:** 0002, 0003, 0004, 0006, 0007, 0009, 0010, 0011, 0014, 0015, 0016, 0017, 0019, 0020.

## Release decision

**Decisão:** `fail`.

**Justificativa:** critério 1 do SPEC §Critério de refutação é violado:
- `hit_rate = 28.13% < 45%` — **violação clara**.

Os critérios 2 (`max_drawdown > 35%`) e 3 (`spread+10` Δ < -5%) **passam** (mdd=8.90% e Δ=-3.75% ambos dentro dos thresholds). Contudo, a regra é boolean OR — qualquer violação refuta. Hipótese §1 também passa apenas parcialmente: `final_equity ≥ 9500` passa em valor absoluto mas é luck-driven (walk-forward test-only soma -556.50). Como critério 1 falha explicitamente, `release_decision = fail`.

> **`live` nunca é opção.** Hook bloqueia, e esta decisão recusa por doutrina também. `paper_only` exigiria módulo `paper-trade` que não existe (vision/02-scope deferred) → efetivamente `fail` mesmo se houvesse edge.

## Condicionais

Piloto **não** vira `paper_only` ou `canary_only` em nenhuma condição realista. Re-avaliação exigiria novo piloto com escopo ampliado:

- Filtro de regime (deferred — módulo `regimes/`).
- Janela de dataset maior (≥1 ano, múltiplos regimes).
- Estratégia diferente (abrir piloto separado).

## Lições aprendidas (para próximos pilotos)

1. **`final_equity ≥ capital` não é sinal de edge.** H.2a preservou capital (+2.4%) mas `hit_rate` e walk-forward indicam ausência de edge. Trade-off: métrica de preservação é ruidosa em N baixo (96 trades); `hit_rate` ≥ 45% é threshold mais robusto. Confirma que o critério 1 do SPEC (hit_rate) é o mais importante dos três.
2. **Propriedade estrutural `fee+Δ ≡ spread+Δ` replica cross-asset.** 2 pilotos × mesmo Δ (10 bps) × mesmo resultado (Δ final_equity idêntico dentro do piloto; proporcional entre pilotos). Evidência empírica forte de ADR-0019 — não bug de BTC, não artifact de dataset.
3. **Monte Carlo p50 < breakeven mesmo quando baseline > breakeven** é sinal de que o ganho do baseline é concentrado em poucos outliers. Estratégia só "funciona" se os outliers acontecem; resampleing mostra que na maioria das reordenações possíveis a equity fica abaixo de 10000.
4. **Walk-forward degradation monotônica** (hit_rate 37.50% → 29.17% → 22.22% → 10.53%) é um sinal forte de que o sinal Donchian puro se dissipa ao longo de 2025. Regime-dependence é aparente mesmo dentro de 180 dias.
5. **Cross-asset signal is noise** dentro de um mesmo regime macro. ETH outperformou BTC em `final_equity` por diferença estrutural (outliers positivos), mas em `hit_rate` a diferença é residual (28.13% vs 25.45%). Sugere que próximos pilotos devem priorizar mudanças de estratégia ou regime antes de varrer ativos.

## Assinatura

- **Auditado por:** `risk-auditor` (agente) em modo autônomo autorizado por sessão 2026-04-17/18; assinatura humana **dispensada** por ser segunda execução do protocolo em continuação direta de H.1 (janela autônoma de 4h ainda ativa).
- **Data:** 2026-04-18 (timestamp UTC do `run.json`).
- **Confirmação humana:** não aplicável — `release_decision = fail` não requer promoção; piloto encerra no gate 5 com documentação e artefatos persistidos. Para qualquer promoção a `paper_only`/`canary_only` (não o caso), assinatura humana é obrigatória por CLAUDE.md §3.

release_decision: fail

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **8/12**
- `composite_score`: **4.70**
- `hit_baseline`: **28.12%** (< piso de 45%)
- `fe_baseline`: **10240.02**
- `flags_digest`: `cf0b670ca2132a50`

**Justificativa:** rank 8/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=28.12% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.

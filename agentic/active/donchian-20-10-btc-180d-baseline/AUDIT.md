# AUDIT.md — Donchian 20/10 BTCUSDT 1h 180d (baseline)

> Gate ativo: **auditoria**. Produzido pelo protocolo após VALIDATION.md + BACKTEST.md. `release_decision` obrigatório; **nunca `live`**.

## Resumo executivo

Donchian 20/10 long-only sobre BTCUSDT 1h 180d **não preserva capital** no regime 2025-07..2025-12 (baseline `final_equity = 9089.79`, -9.1%; `hit_rate = 25.5%` vs limiar de 45% declarado no SPEC). 3 de 4 folds do walk-forward são negativos; Monte Carlo tem p95 = 9716 (ou seja, menos de 5% dos resamples chegam a 97.16% do capital inicial, e nenhum percentil p5-p95 atinge breakeven). Estratégia é **refutada** pelos próprios critérios do SPEC — decisão natural é `fail`.

## Blockers

Itens que **reprovam** o piloto hoje. Cada item é factual com referência cruzada.

1. **`hit_rate = 25.45%` viola SPEC §Critério de refutação item 1** (limiar ≥ 45%). Evidência: `results/validation/donchian-20-10-btc-180d-baseline/cost_stress.json → baseline.result.metrics.hit_rate = 0.2545`. Remediação: não há — hit-rate é propriedade emergente; seria necessário ou (a) mudar janelas 20/10 (novo piloto com ADR justificando tuning), ou (b) adicionar filtro de regime (fora de escopo atual, precisaria de módulo `regimes/` — hoje deferred).

2. **`final_equity = 9089.79 < 9500`** (SPEC §1 hipótese afirma preservação de 95% do capital). Embora não seja critério formal de refutação, é violação direta da hipótese afirmativa. Evidência: `cost_stress.json → baseline.result.final_equity`.

3. **3 de 4 folds walk-forward com pnl negativo.** Evidência: `walk_forward.json` mostra pnl=(-156.03, +10.64, -247.51, -327.91) para folds 1-4. Único fold positivo (fold 2) entrega apenas +10.64 USDT, dentro da margem de ruído estatístico de 21 trades. Remediação: não há — indica ausência de edge no período, não bug de execução.

4. **Monte Carlo p95 < capital inicial (9716 < 10000).** Evidência: `monte_carlo.json → payload.final_equity_percentiles["95"] = 9716.27`. Probabilidade empírica de `final_equity ≥ 10000` é <<5% sobre 500 resamples com seed=42. Distribuição inteira do PnL resample está abaixo de breakeven.

## Riscos operacionais

Estes não são blockers **porque** o piloto já falhou em `backtest_only` — não há risco operacional a mitigar em paper/live. Listados para rastreabilidade:

1. **Bug Windows cp1252 em `cli/app.py:672`** — `→` em print quebra sem `PYTHONIOENCODING=utf-8`. Documentado em VALIDATION.md §Falhas conhecidas e IMPLEMENTATION.md §Nota operacional. Não bloqueia este piloto (usado workaround); candidato a patch em `src/` fora do escopo do protocolo agentic (infra issue, não decisão de estratégia).

## Compliance do laboratório

Checklist item por item:

- [x] `LIVE_TRADING=false` confirmado em código/config — nenhuma var de ambiente `LIVE_TRADING=true` presente; hook `.claude/hooks/block_live_trading.py` bloquearia.
- [x] Hard cap de alavancagem (≤10x) respeitado — `alavancagem=2.0` no `run.json`.
- [x] Sizing é fixed fractional (ADR-0004) — `fracao=0.1` + `alavancagem=2.0`; notional constante 2000 USDT em todos os fills verificados. Sem martingale/averaging/grid oculto.
- [x] Nenhum `import ccxt`/`binance.client`/`.create_order` em `src/` — grep -r = 0 matches (hook PreToolUse preveniria).
- [x] Secrets fora do repo (`.env`, chaves, credenciais) — `.claude/settings.json → permissions.deny` bloqueia edição de `.env*`, `**/*.pem`, `**/*.key`, `**/credentials*`.
- [x] Paper/live **não** tratado como se existisse — `release_decision ∈ {fail, paper_only, canary_only}`; paper_only hoje é efetivamente `fail` porque módulo `paper-trade` não existe (vision/02-scope deferred).
- [x] Testes property-based de causalidade verdes, OHLCV completo — suíte `289/1skip`, `tests/property/test_lookahead_guard.py` verde.
- [x] Monotonicidade de custo (ADR-0010 + ADR-0019) verde nos 3 eixos — cost_stress scenarios têm `final_equity ≤ baseline` em fee+10, slip+5, spread+10; confirmado em BACKTEST.md §Sensibilidade.
- [x] `walk_forward.json`, `monte_carlo.json`, `cost_stress.json`, `run.json` persistidos (ADR-0015 + ADR-0017) em `results/validation/donchian-20-10-btc-180d-baseline/`.

## Evidências consultadas

- **Arquivos lidos:**
  - `results/validation/donchian-20-10-btc-180d-baseline/run.json` (flags + metadados)
  - `results/validation/donchian-20-10-btc-180d-baseline/walk_forward.json` (4 folds)
  - `results/validation/donchian-20-10-btc-180d-baseline/monte_carlo.json` (500 resamples, seed=42)
  - `results/validation/donchian-20-10-btc-180d-baseline/cost_stress.json` (baseline + 3 cenários)
  - `agentic/active/donchian-20-10-btc-180d-baseline/SPEC.md` (critério de refutação)
  - `agentic/active/donchian-20-10-btc-180d-baseline/IMPLEMENTATION.md` (mapeamento SPEC→código)
  - `agentic/active/donchian-20-10-btc-180d-baseline/VALIDATION.md` (conformidade)
  - `agentic/active/donchian-20-10-btc-180d-baseline/BACKTEST.md` (métricas + sensibilidade)
- **Testes rodados:** `python -m pytest -q` → 289 passed, 1 skipped (estado base; piloto não altera `src/`).
- **Comandos executados:**
  - `PYTHONIOENCODING=utf-8 python -c "from alpha_forge.cli import app; ..."` (pipeline `validate`)
  - `python scripts/validate_artifacts.py` (confirmação — ver CHECKLIST.md)
- **ADRs consultadas:** 0002 (causalidade), 0003 (walk-forward + MC), 0004 (sizing), 0006 (custos mínimos), 0007 (métricas), 0009 (dataset), 0010 (monotonicidade), 0011 (Donchian), 0014 (cost_stress), 0015 (persistência), 0016 (CLI validate), 0017 (run metadata), 0019 (spread), 0020 (overlay agentic).

## Release decision

**Decisão:** `fail`.

**Justificativa:** dois critérios independentes do SPEC §Critério de refutação são violados:
1. `hit_rate = 25.45% < 45%` (refutação item 1) — **violação clara**.
2. `final_equity = 9089.79 < 9500` — viola a hipótese afirmativa do SPEC §1 (preservação de 95% do capital).

O terceiro critério (`spread+10` Δ < -5% contra baseline) **passa por margem estreita** (-4.81% vs limiar -5%), mas a margem é insignificante dado que os critérios 1 e 2 já falharam.

> **`live` nunca é opção.** Hook bloqueia, e esta decisão recusa por doutrina também. `paper_only` exigiria módulo `paper-trade` que não existe (vision/02-scope deferred) → efetivamente `fail` mesmo se houvesse edge. Com os critérios violados, o caminho operacional também é `fail` sem ambiguidade.

## Condicionais

Este piloto **não** vira `paper_only` ou `canary_only` em nenhuma condição realista de curto prazo. Para virar candidato a re-avaliação, precisaria de novo piloto com escopo ampliado:

- Filtro de regime (deferred — precisa módulo `regimes/`).
- Janela de dataset maior (≥1 ano, capturando múltiplos regimes de bull/bear/lateral).
- Ou estratégia diferente (ex: Donchian 55/20 convencional, não 20/10) — abriria piloto separado.

## Lições aprendidas (para próximos pilotos)

1. **Donchian 20/10 em janela lateral é adverse selection.** Pequenas janelas pegam mais sinais falsos que grandes; `exit_window=10` curto força saída antes do movimento consolidar.
2. **hit_rate 25% com 110 trades em 180 dias sugere regime filter ausente é o gap central**, não as janelas per se.
3. **fee+10 ≡ spread+10 em impacto de equity** (ambos Δ=-437.73) — resultado estrutural do modelo de custo quando `notional/capital_inicial` é constante. Reforça que o eixo de spread (ADR-0019) captura uma dimensão real de custo.
4. **Monte Carlo percentis p5-p95 todos sub-breakeven** é sinal forte de ausência de edge, independente de variância de sequência.

## Assinatura

- **Auditado por:** `risk-auditor` (agente) em modo autônomo autorizado por sessão 2026-04-17; assinatura humana **dispensada** por esta ser a primeira execução do protocolo (piloto de validação da infra, não release real de estratégia).
- **Data:** 2026-04-18 (timestamp UTC do `run.json`).
- **Confirmação humana:** não aplicável — `release_decision = fail` não requer promoção; piloto encerra no gate 5 com documentação e artefatos persistidos para auditoria futura. Para qualquer promoção a `paper_only`/`canary_only` (não o caso), assinatura humana é obrigatória por CLAUDE.md §3.

release_decision: fail

---

## Re-auditoria 2026-04-18 (ADR-0025)

release_decision: fail

**Critério vigente:** híbrido (ADR-0025) — `canary_only` exige `hit_rate ≥ 45%` absoluto; `paper_only` exige top-3 por `composite_score` (ADR-0024) com N ≥ 9.

**Snapshot de ranking (2026-04-18, DEFAULT_WEIGHTS de ADR-0024):**

- Rank: **10/12**
- `composite_score`: **3.89**
- `hit_baseline`: **25.45%** (< piso de 45%)
- `fe_baseline`: **9089.79**
- `flags_digest`: `57e54a79f1fe3901`

**Justificativa:** rank 10/12 por `composite_score`; fora do top-3 → permanece `fail` sob ADR-0025. `hit_rate`=25.45% < 45% também impede `canary_only`.

**Decisão original preservada acima.** Esta seção é append imutável; revogações futuras devem ser **nova seção**, nunca edit.

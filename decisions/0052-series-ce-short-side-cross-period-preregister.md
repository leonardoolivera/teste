# 0052 — Série CE: Bollinger + RSI short side cross-period (pré-registro)

**Status:** Accepted — pré-registro; execução inicia imediatamente
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0049 (meta-análise CA-CD), ADR-0050 (vocabulário), ADR-0051 (short side Bollinger/RSI).

## Context

ADR-0049 consolidou 4 séries cross-period (CA/CB/CC/CD, 46+ runs) mostrando que edge estrutural long-only colapsa fora de recorte fixo. ADR-0050 identificou **short side** como única expansão de vocabulário com payoff esperado positivo no curto prazo (Tier 2). ADR-0051 implementou short em Bollinger e RSI (simétrico, reverse-on-signal herdado de ADR-0012).

Duas hipóteses concorrentes de ADR-0049 a serem falsificadas:

- **H1 (otimista)** — short resgata o projeto: se bull long-only morreu e chop long-only não paga custo, talvez o edge estivesse na direção **oposta** o tempo todo (mean-reversion pra baixo em bull extendido, overbought ficando overbought). Série CE ≥6/18 passando separa H1 de H2.
- **H2 (pessimista)** — regime domina; short também colapsa cross-period. CE < 3/18 confirma que **o problema é temporal, não direcional**. Pivota pra ADR-0050 §D3 (volatility-adjusted sizing) ou §D5 (regime-gated ensemble) na próxima ADR.

Esta série é **falsificacionista**: o melhor resultado possível **ainda** é pequeno (6-9 de 18) comparado a baseline long+filtro do manifest. Se CE passar o Gate 1, é **evidência** pra desenvolver short, não aprovação pra manifest.

## Decisão

Executar 18 pilotos short-only (`long_only=False`) cross-period com gates pré-registrados. Nenhum filtro arquitetural (isolar o short puro — filtro de volatilidade fica pra série posterior se CE passar).

### Matriz de pilotos

| # | Recorte | Dataset-id sufixo | Ativo | Regime rótulo (heurístico) |
|---:|---|---|---|---|
| CE.1 | 2024-H2 | `20240705_20241231` | BTC | bull forte |
| CE.2 | 2024-H2 | `20240705_20241231` | ETH | bull forte |
| CE.3 | 2024-H2 | `20240705_20241231` | SOL | bull forte |
| CE.4 | 2025-H1 | `20250105_20250704` | BTC | chop/correction |
| CE.5 | 2025-H1 | `20250105_20250704` | ETH | chop/correction |
| CE.6 | 2025-H1 | `20250105_20250704` | SOL | chop/correction |
| CE.7 | 2025-H2 | `20250705_20251231` | BTC | bull moderado |
| CE.8 | 2025-H2 | `20250705_20251231` | ETH | bull moderado |
| CE.9 | 2025-H2 | `20250705_20251231` | SOL | bull moderado |

**Cada piloto roda 2 variantes**: `bollinger 20/1.5` e `rsi 14 os=30 ob=70`. Total **18 runs**.

Parâmetros de estratégia são os **mesmos do manifest histórico** (Bollinger 20/1.5 é parâmetro base da família, RSI 14/30/70 é default canônico). Não é grid-search. Alinhado com ADR-0049 §Padrão 5 ("não grid, não post-hoc").

### Parâmetros de engine (idêntico a CA-CD — compatibilidade cross-série)

- capital 10000, fracao 0.1, alavancagem 2.0
- taker 5bps, slippage 2bps, spread 0
- n-folds 5, rolling, train_fraction 0.5, min_test_bars 50
- mc_resamples 1000, mc_seed 42
- stress `fee+10:10:0:0`, `spread+10:0:0:10`
- regime_filter: **none** (short puro)
- `--no-long-only`

### Gates pré-registrados

**Gate 1 — principal (PASS/FAIL da série)**: ≥ **6/18** pilotos passando **todos**:

- trades ≥ 30 (OOS walk-forward agregado)
- Sharpe ≥ 1.0
- MDD ≤ 20
- MC p5 > 9500
- cost_stress_ratio ≥ 0.95

Gate 1 == critério de promoção do manifest v2 atual. Se 6/18 passam, **short é material** e merece Série CE+1 com filtro. Se < 6/18, short puro é insuficiente.

**Gate 2 — falsificacionista (sanidade)**: em 2024-H2 (bull forte, 3 ativos × 2 estratégias = 6 pilotos), **≤ 1/6 deve passar Gate 1**. Se ≥ 2/6 passarem, investigar: (a) marcação de regime errada, (b) edge não é regime-dependente como previsto, (c) artefato de cálculo. Bull forte é *adversário natural* de short em mean-reversion de crypto.

- **Como aplicar**: se Gate 2 falhar (≥2/6 em 2024-H2), **pausar série** e investigar antes de aceitar Gate 1. Gate 2 é *coerência*, não viabilidade.

**Gate 3 — regime preferido (diagnóstico)**: em 2025-H1 (chop, 6 pilotos), **≥ 3/6 devem passar Gate 1**. Se 2025-H1 não for o melhor recorte, hipótese "chop = amigo de short" falha, e `trend_htf:mode=short_only` (amplificar short em chop) também é fantasia.

- **Como aplicar**: Gate 3 isoladamente não promove/descarta; serve pra *orientar* próxima ADR (qual filtro casa com short).

**Gate 4 — assimetria Bollinger vs RSI (diagnóstico)**: entre 9 Bollinger e 9 RSI, contar quantos passam Gate 1. Se diferença > 3, a estratégia "melhor pra short" é discriminada — vira input pra ADR de promoção.

### Tooling

- `tools/run_ce_sweep.py`: sweep com os 18 runs, `run_id = ce-<strat>-<asset>-<suffix>-short`
- `tools/summarize_ce.py`: agrega walk_forward/monte_carlo/cost_stress, aplica Gates 1-4, outputs `exports/diag/ce_series_summary.json`

### Regras de não-movimento de régua

- Gates 1-4 **não podem ser renegociados** após a execução. Se Gate 1 der 5/18, FAIL; não "quase passou".
- Se algum piloto falhar por erro técnico (dataset ausente, NaN, etc.), re-rodar o piloto exato, não relaxar o gate.
- Sharpe calculado via `summarize_ce.py` usa o mesmo pipeline equity-curve de ADR-0048 (§Nota de reconciliação) — valor oficial. Diferença vs pipeline trade-based do manifest é esperada ~4%.

### Timebox

- Execução dos 18 runs: ~30-40min (sweep sequencial; mesmas dimensões de CA-CD).
- ADR-0053 closeout escrita no mesmo dia.

## Hipóteses explícitas (pré-registradas)

1. **H-principal**: short puro passa Gate 1 em **~6-9/18**. Razão: short em overbought é simétrico a long em oversold, que passou no manifest v2 (4/15); em 2025-H1 (chop) especificamente, short deve ser *mais* produtivo que long (reversão pra baixo é o regime dominante em correções).
2. **H-falsificação** (Gate 2): 2024-H2 mata short. Razão: bull extendido significa "cada sinal overbought é continuação, não reversão". Gate 2 testa se o universo se comporta como crypto historicamente se comporta.
3. **H-regime**: 2025-H1 > 2025-H2 > 2024-H2 (ranking esperado de pass-rate). Razão: chop > bull moderado > bull forte pra mean-rev short.
4. **H-assimetria**: Bollinger > RSI em short (ADR-0048 mostrou que Bollinger tem composição produtiva quando Width filter corta falso-sinal; sem filtro, Bollinger ainda é o template preferido pra mean-rev em crypto).

Se H1 e H2 forem consistentes (Gate 1 + Gate 2 ambos PASS), **H2 de ADR-0049 é falsificada** — regime não é totalmente dominante; existe *um* vocabulário direcional válido (short mean-rev).

Se Gate 1 FAIL com Gate 2 PASS (H-falsificação confirmada, mas H-principal falha), **H2 de ADR-0049 é fortalecida** — regime domina, curva 2024-H2 do manifest foi *sorte do recorte*.

## Saída da série

- Manifest **não muda** nesta ADR. Promoção requer ADR separada + Série CE+1 com filtro composicional (Bollinger+BollingerWidthFilter em modo short, ou similar).
- Bot BotBinance não é notificado até fechar ADR-0053 (signal-only rule: notificar só se muda decisão do bot — e durante pesquisa não muda).

## Alternativas consideradas

### Rodar 27 pilotos (3 recortes × 3 ativos × 3 estratégias, incluindo ma_crossover short)

Rejeitado. ma_crossover é trend-following — short em trend-following significa "vender após cruzamento de baixa", que é continuation, não mean-reversion. Semanticamente diferente. Se H-principal passar pra mean-rev, ADR futura pode testar ma_crossover short em comparação, mas misturar na mesma série embaraça a leitura.

### Incluir BollingerWidthFilter no piloto (espelhando manifest v2)

Rejeitado nesta série. Meta-análise (ADR-0049 §Padrão 3) distingue edge bruto de edge composicional. Medir short **puro** primeiro, depois (se passar) adicionar filtros. Faz o contrário = confundir as duas fontes de edge.

### Incluir 2023-H2 e 2024-H1 no cross-period

Rejeitado. CA-CD já estabeleceram que 2024-H2 é o piloto forte do manifest; 2025-H1/H2 é out-of-sample. 2023-H2 e 2024-H1 têm overlap com in-sample original do manifest — introduz contaminação. Série CE mantém a disciplina de CA-CD de testar **apenas** em recortes out-of-sample relativos ao piloto forte 2024-H2.

### Gate 1 em 4/18 em vez de 6/18

Rejeitado. 4/18 ≈ 22%; isso é equivalente a "1-2 passes por recorte", que é indistinguível de sorte em 9 pilotos por recorte. 6/18 (33%) = 2 passes por recorte em média — passa do ruído, indica estrutura. Espelho da densidade do manifest v2 (4/15 ≈ 27%, que **também** é baixa — mas está no borderline superior, conforme audit ADR-0048).

## Consequences

**Positive:**
- Primeira avaliação sistemática do short side em todo o projeto.
- Resolve disputa H1 vs H2 de ADR-0049 com evidência empírica.
- Baixo custo (~30min de compute + 2 ADRs).

**Negative:**
- Se Gate 1 PASS, ainda não é aprovação — requer +1 série composicional antes de manifest. Ciclo longo.
- Se Gate 1 FAIL com Gate 2 PASS, reforça hipótese pessimista — próxima ADR terá que pivotar pra abordagens mais ambiciosas (vol-adjusted sizing, regime-gated ensemble) que têm payoff mais incerto.

**Neutral:**
- ADR-0053 fecha série independente do resultado. Conteúdo varia mas existe.

## Critério de sucesso (da execução da série)

1. 18 runs rodam sem crash.
2. `summarize_ce.py` produz saída interpretável (Gates 1-4 avaliados).
3. ADR-0053 discute resultado e aciona H1 ou H2 de ADR-0049.

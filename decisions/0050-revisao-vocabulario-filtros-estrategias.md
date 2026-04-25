# 0050 — Revisão do vocabulário: filtros e estratégias

**Status:** Accepted — revisão; abre eixos novos sem implementá-los
**Date:** 2026-04-19
**Deciders:** Usuário + agente.
**Relates to:** ADR-0049 (meta-análise), vision/01-product.md, vision/02-scope.md.

## Context

A meta-análise (ADR-0049) concluiu:

> "O problema não é de execução, é de vocabulário."

4 séries cross-period (CA/CB/CC/CD) + audit confirmaram: o universo atual de 3 estratégias × 4 filtros não gera edge cross-period estável. Duas hipóteses concorrentes:

- **H1** — edge estável não existe neste universo (BTC/ETH/SOL 1h, long-only, 180d).
- **H2** — edge existe mas exige vocabulário ausente.

Esta ADR **não decide** entre H1 e H2. Ela inventaria o vocabulário atual, identifica lacunas auditáveis frente a `vision/02-scope.md`, e prioriza eixos candidatos pra expansão. Cada eixo novo é **candidato a ADR futura** (implementação) ou **candidato a descarte explícito** (adiciona nota nos non-goals).

## Inventário atual

### Estratégias (5 famílias, todas long-only, todas LTF 1h)

| Família | Arquivo | Edge teórico | Status empírico |
|---|---|---|---|
| `dummy` | `strategies/families/dummy/` | — | Sanity estrutural |
| `ma_crossover` | `strategies/families/ma_crossover/` | Trend (slope) | Testado em Séries antigas |
| `donchian` | `strategies/families/donchian/` | Breakout trend | CA FAIL 2/10, CD FAIL 1/9 |
| `bollinger` | `strategies/families/bollinger/` | Mean-reversion | CC FAIL 0/9; manifest SOL 2024-H2 PASS (+filtro width) |
| `rsi` | `strategies/families/rsi/` | Mean-reversion momentum | CB FAIL 2/9 |

### Filtros (4 no `regimes/filter.py`)

| Filtro | Dimensão capturada | Ortogonal a quem? |
|---|---|---|
| `SMASlopeFilter` | Direção da tendência LTF (slope de SMA) | Não-ortogonal a `ma_crossover` strategy |
| `ATRRegimeFilter` | Volatilidade de candle (true range) | Ortogonal a width, trend_htf |
| `BollingerWidthFilter` | Volatilidade estrutural (spread de banda) | Ortogonal a ATR, trend_htf. **Não-ortogonal a `bollinger` strategy** (ADR-0049 §Padrão 3) |
| `TrendHTFRegimeFilter` | Direção HTF (4h/1d/1w close vs SMA HTF) | Ortogonal aos 3 acima |

### Composição (ADR-0023)

- `CompositeFilter(mode="and"|"or")` — 1 nível de aninhamento, ≥2 filtros, sem duplicatas.
- **Sem sintaxe CLI ainda** pra composição (só via código — ver ADR-0043 §"Fora desta ADR").

### Métricas / scoring

- Walk-forward (ADR-0003), Monte Carlo i.i.d. trades (ADR-0003), Cost Stress (ADR-0014).
- Ranking composite com 7 pesos (ADR-0024), release_decision {fail, paper_only, canary_only}.

## Lacunas frente a `vision/02-scope.md`

`02-scope.md` promete 10 famílias de estratégia e 8 regimes auditáveis. Inventário vs promessa:

### Famílias prometidas vs implementadas

| Prometido em scope.md | Implementado? | Gap |
|---|---|---|
| Breakout | ✓ Donchian | — |
| Momentum | Parcial (RSI) | Faltam variantes puras |
| Pullback | ✗ | **Ausente** |
| Mean reversion | ✓ Bollinger, RSI | — |
| Liquidity sweep | ✗ | **Ausente** (precisa orderbook?) |
| Continuação | ✗ | **Ausente** |
| Expansão de range | ✗ | **Ausente** |
| Snowball | ✗ | **Ausente** (sizing, não só sinal) |
| Falha de rompimento | ✗ | **Ausente** |
| Híbrida | ✗ | **Ausente** (composição de sinais) |

**5/10 famílias ausentes**. Algumas são composições triviais (falha-de-rompimento = Donchian short + confirmação); outras exigem infraestrutura nova (snowball = sizing dinâmico).

### Regimes prometidos vs implementados

`vision/02-scope.md` lista 8 regimes (tendência alta/baixa forte, lateral alta/baixa vol, compressão, expansão, pânico, euforia). **Nenhum classificador de regime existe** — temos 4 **filtros** (boolean per-bar), não um **classificador de regime multi-estado**. `TrendHTFRegimeFilter` é o mais próximo (bias direcional HTF), mas ainda é filtro, não classifier.

**Gap estrutural**: o produto promete "classificação por regime" como diferencial #3 em `01-product.md`. Hoje, o que temos é **boolean filter per-bar**, não atribuição de regime.

### Capabilities ausentes das estratégias

`strategies/02-scope.md §Module: strategies` promete:

- interface padrão **long/short** — hoje é long-only em 100% das estratégias
- stop fixo / ATR / trailing — **engine não suporta stops explícitos** (ordens são sinais binários)
- takes parcial e final — **ausente**
- break-even — **ausente**
- pyramiding opcional — **ausente**

**Gap crítico**: o engine trata sinal como "all-in / all-out" com `fracao=0.1` fixo. Stops, takes, pyramiding e trailing **não existem**. Snowball, que vision.md lista como família, precisa disso.

## Taxonomia de gaps (por custo de implementação)

### Tier 1 — gaps que cabem no engine atual (baixo custo)

Eixos implementáveis sem mudar arquitetura; só ADR + código.

1. **Pullback strategy** — detectar retração em trend confirmado (ex: close > SMA 200 AND close < SMA 20 AND RSI < 40). Estratégia long-only, stateless, 1 sinal por barra. Custo: **~1 dia**. Valor: testa "composição trend+mean-rev no LTF" sem ir pra HTF.
2. **Falha de rompimento** — Donchian breakout **invertido** (rompe entry window e volta pra dentro em N barras). Sinal contra-breakout. Custo: **~1 dia**. Valor: complementar a Donchian; testa universo de "armadilhas de breakout" que é específico de cripto.
3. **Composição CLI de filtros** (ADR-0043 §fora de escopo) — sintaxe `--regime-filter "and(f1:...,f2:...)"`. Já existe em código (CompositeFilter); falta parser CLI. Custo: **~0.5 dia**. Valor: habilita experimentação sem code.
4. **Sintaxe CLI pra composição de estratégias** — rodar 2 estratégias no mesmo run e agregar sinais por AND/OR. Custo: **~1 dia**. Valor: testa "hybrid strategy" de scope.md sem criar nova família.

### Tier 2 — gaps que exigem extensão do engine (médio custo)

1. **Short side ativo** — engine já tem `ENTER_SHORT` (ADR-0013, Donchian simétrico). Falta ativar em Bollinger/RSI/família nova e re-validar. **Filtros direcionais (`trend_htf:short_only`) ganham sentido**. Custo: **~2-3 dias** (código + validação + manifest). Valor: **alto** — dobra o universo observável sem novos ativos. ADR-0049 §Padrão 7 identifica esse gap.
2. **Stops explícitos no engine** — ordens SL/TP além de sinais binários. Extensão não-trivial do backtest core (ADR-0006 limita escopo atual). Custo: **~5-7 dias**. Valor: **alto** — habilita stop fixo/ATR/trailing, take parcial, break-even, que são diferenciais prometidos pelo vision/01-product §#4. Mas é ADR própria grande (risco fora de scope desta revisão).
3. **Sizing dinâmico por regime** (ADR-0049 §Padrão 6) — `fracao` muda com filtro ativo/inativo. Complementa `trend_htf` existente. Custo: **~2 dias**. Valor: médio-alto — destrava o "lift de risco sem lift de retorno" observado em CC/CD.

### Tier 3 — gaps arquiteturais (alto custo, alta incerteza)

1. **Classifier de regime multi-estado** — substituir/complementar os boolean filters por atribuição {trend_up_strong, range_low_vol, expansion, panic, euphoria} per-bar. Vision/01-product §#3 promete isso como diferencial. Custo: **7-15 dias** (depende de método: regras vs ML). Valor: **altíssimo** — primeiro diferencial arquitetural vs frameworks genéricos. Risco: alto (ML vira dependência; regras podem não bater promessas).
2. **Cross-asset context** — feature de outros ativos no engine (ex: BTC direction como filtro pra ETH signal). Exige mudança no `RegimeFilter` Protocol (hoje recebe só 1 window). Custo: **3-5 dias**. Valor: médio — testaria hipótese "edge LTF exige contexto macro".
3. **Multi-TF native strategies** — estratégias que leem 1h + 4h + 1d nativamente, sem filtro HTF como patch. `trend_htf` é patch. Native exigiria mudar API de `Strategy.decide(window)` pra receber múltiplas windows. Custo: **5-10 dias**. Valor: médio — conceitualmente limpo, mas overlaps com classifier (Tier 3.1).
4. **Portfolio layer** — AF hoje produz sinal único; ADR-0049 §Padrão 6 mostra que "lift de risco sem retorno" é inútil sem portfolio. Portfolio seria camada nova (agregador de sinais + alocação). Custo: **10+ dias**. Valor: depende da direção do projeto — se AF é "laboratório de estratégias", portfolio é fora de escopo; se é "motor de decisão multi-estratégia", é núcleo.

## Decisões desta ADR

### Decisão 1 — Não adicionar estratégia pura antes de expandir eixo arquitetural

Abrir mais série LTF long-only com estratégia nova seria sweep quinto seguido. Depois de 4 FAILs, diminishing returns é óbvio. **Pullback e falha-de-rompimento (Tier 1) ficam em espera**, abertos via ADR futura mas não são próxima série.

### Decisão 2 — Próxima expansão arquitetural: **short side** (Tier 2.1)

Justificativa:

- **Dobra o universo observável** com 0 novos ativos, 0 novos recortes, 0 novas estratégias. Todo o dataset atual vira testável em 2 direções.
- **Desbloqueia `trend_htf:short_only`** — metade do filtro hoje é inacessível (ADR-0049 §Padrão 7). Short side torna o filtro simétrico.
- **Engine já suporta parcial** (ADR-0013 Donchian). Extensão pra Bollinger/RSI e manifest é incremental.
- **Custo baixo** (~2-3 dias) vs valor estrutural alto.
- **Risco controlado**: se falhar, informa sem custo altíssimo; se passar, amplia manifest sem novo universo de dados.

Pré-requisito: **ADR de implementação short side** (código + validação). Não é parte desta ADR-0050.

### Decisão 3 — Classifier de regime fica em espera estratégica (Tier 3.1)

`vision/01-product.md §#3` promete classifier. Hoje temos 4 boolean filters. Gap é real e diferencia o produto. **Mas**:

- Custo 7-15 dias, alto vs caixa de tempo atual.
- Risco de virar "mini-AutoML" (vision/01-product §non-goals proíbe).
- Sem short side, classifier é metade-útil (mesmo motivo que `trend_htf`).

Portanto: **classifier depende de short side primeiro**. Se short side PASS + manifest cresce, classifier vira ADR candidata após. Se short side FAIL, classifier ganha prioridade (porque mais vocabulário não resolveu; reorganização do vocabulário existente pode).

### Decisão 4 — Composição CLI de filtros (Tier 1.3) entra como tarefa paralela baixa prioridade

Já tem código; falta só parser. Útil imediatamente (pre-registro CC já usou composição AND, mas só conseguiu via Python). ADR pequena (~0.5 dia). Pode ser feita por qualquer agente em janela livre. **Não bloqueia short side**.

### Decisão 5 — Stops explícitos, sizing dinâmico, cross-asset, multi-TF, portfolio ficam explicitamente fora do roadmap curto

Custos 3-10+ dias, fora da janela atual. Cada um merece ADR própria quando/se virar prioridade. **Não são non-goals** (vision/01-product não proíbe) — são "deferred com justificativa".

### Decisão 6 — Vision.md / scope.md permanecem intocados nesta ADR

Vision é "target", não "state". Que scope promete 10 famílias e 8 regimes e só temos 4+4 é **esperado** — esse é o gap entre aspiração e realidade. Não reescrevo vision pra acomodar implementação.

Se algum gap virar **deliberadamente abandonado** (ex: HFT nunca entra), atualizaria non-goals. Não é o caso de nenhum item acima.

## Matriz resumo

| Eixo | Tier | Custo | Valor | Decisão |
|---|---|---|---|---|
| Short side ativo | 2 | 2-3d | Alto | **Próxima ADR de implementação** |
| Composição CLI de filtros | 1 | 0.5d | Médio | Paralelo, baixa prioridade |
| Pullback strategy | 1 | 1d | Médio | Espera pós-short side |
| Falha de rompimento | 1 | 1d | Médio | Espera pós-short side |
| Hybrid CLI strategies | 1 | 1d | Médio | Espera pós-short side |
| Sizing dinâmico | 2 | 2d | Médio | Espera (sem portfolio, gain limitado) |
| Stops explícitos | 2 | 5-7d | Alto | ADR separada grande; não imediato |
| Classifier de regime | 3 | 7-15d | Muito alto | Depende de short side primeiro |
| Cross-asset context | 3 | 3-5d | Médio | Deferred |
| Multi-TF native strategies | 3 | 5-10d | Médio | Deferred |
| Portfolio layer | 3 | 10+d | Condicional | Deferred; depende de direção |

## Consequences

**Positive:**
- Vocabulário atual inventariado contra vision.md. Gaps são conhecidos e priorizados, não implícitos.
- Próxima implementação (short side) é **ortogonal às 4 séries** — não repete sweep, abre eixo novo com custo/valor claros.
- Decisões #3 e #5 evitam armadilhas conhecidas (AutoML, portfolio sem necessidade).

**Negative:**
- Vocabulário seguirá incompleto vs vision.md por mais algumas ADRs. Vision continua como "target", não "reached".
- 3 famílias Tier 1 (pullback, falha-de-rompimento, hybrid) ficam em fila — oportunidade de edge lá pode envelhecer.

**Neutral:**
- ADRs 0043 (trend_htf) e anteriores permanecem relevantes — trend_htf vira mais útil com short side.
- Manifest v2 continua como está.

## Fora do escopo desta ADR

- Implementação real de qualquer eixo (cada um precisa ADR própria de implementação).
- Decisão sobre H1 vs H2 da ADR-0049 (§Context). Short side é teste instrumental: se passar, evidência pra H2; se falhar, reforça H1.
- Ordem de execução das ADRs seguintes após short side — depende do resultado.
- Bridge AF↔bot: signal-only rule; nada muda no bot até manifest mudar.

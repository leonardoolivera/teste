# 0086 — Série CR closeout: TrendHTF cross-asset FAIL 0/2 → Padrão 14 confirmado (SOL-específico)

**Status:** Accepted — não-promoção, Padrão 14 reforçado
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0085 (pré-registro CR), ADR-0084 (v6 SOL 2025-H1 ativado), ADR-0083 (CP closeout + Padrão 19), Padrão 14 (filter direcional asset-específico)

## Resultado

### CR pilotos (RSI short + TrendHTF short_only) + Gate B naked

| Tag | Asset | Variant | Trades | Sharpe | MDD% | MC p5 | cost_r | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---|
| CR.1-trend | BTC 2025-H1 | trend | 46 | **−0.348** | 5.61 | 9175 | 0.9719 | **FAIL** (Sh, MCp5) |
| CR.1-naked | BTC 2025-H1 | naked | 82 | **+0.233** | 4.08 | 9460 | 0.9564 | **FAIL** (Sh, MCp5) |
| CR.2-trend | ETH 2025-H1 | trend | 62 | **+1.391** | 4.89 | 9429 | 0.9665 | **FAIL** (MCp5) |
| CR.2-naked | ETH 2025-H1 | naked | 100 | **+0.550** | 7.25 | 8780 | 0.9492 | **FAIL** (Sh, MCp5, costr) |

### Referência (manifest v6 ativo, SOL 2025-H1)

| Combo | Variant | Trades | Sharpe | MC p5 | Verdict |
|---|---|---:|---:|---:|---|
| v6 SOL 2025-H1 | trend | 51 | **+1.958** | 9712 | **PASS** |
| naked SOL 2025-H1 | naked | 90 | 0.615 | 8946 | FAIL |

## Avaliação dos gates pré-registrados

### Gate 1 (≥1/2 PASS): **FAIL 0/2**

- CR.1 BTC trend Sh=−0.35 → RSI short destrutivo em BTC 2025-H1 com trend
- CR.2 ETH trend Sh=1.39 **mas MC p5=9429** (< 9500) — falha estatística robustness

### Gate 2 (lift sobre incumbente v4a BTC width Sh=1.688): **FAIL**

- CR.1 BTC trend (−0.35) vs v4a BTC width (+1.69) → delta −2.04 (destrói edge)
- ETH sem incumbente (não aplicável)

### Gate 3 (load-bearing vs naked — Padrão 19): **FAIL 0/2**

- **BTC:** trend Sh=−0.35 vs naked Sh=+0.23 → **trend é PIOR que naked**. Filter não-carrega edge; trend *destrói* edge marginal do naked em BTC.
- **ETH:** trend Sh=+1.39 vs naked Sh=+0.55 → trend lift (+0.84). MAS: trend também FAIL Gate 1 (MC p5<9500). Então Gate 3 é tecnicamente inconclusivo — trend "sobe o Sh" mas não passa o gate.

### Gate 4 — Promoção: **BLOQUEADA 0/2**

Nenhum combo PASS Gate 1. Nenhum load-bearing estrito. v6 **permanece 1 combo apenas** (SOL 2025-H1).

## Interpretação

**TrendHTF short_only é SOL-específico em 2025-H1 chop.** Padrão 14 confirmado cross-asset:
- BTC 2025-H1: trend destrói edge (−2.04 Sh vs naked e vs width). Filtro direcional remove trades que em BTC estão ok-neutras; o que sobra é piorado.
- ETH 2025-H1: trend tem lift direcional (+0.84 vs naked) mas amostra pós-filtro é 62 trades com MC p5 9429 — não robusto.
- SOL 2025-H1 (v6): trend é load-bearing (naked 0.62→1.96 FAIL→PASS). **Única janela × asset × regime onde trend-only funciona.**

**Hipótese reforçada:** SOL é alt alta-beta com reversões chop mais pronunciadas em downtrend HTF; BTC e ETH têm microestrutura chop diferente (BTC: menos reversão em downtrend; ETH: reversão presente mas sample insuficiente pós-filtro). Filter direcional amplifica setups onde correlação regime-HTF × reversão é forte — SOL é o caso extremo.

## Decisão

### Não-promoção CR.1 e CR.2

v6 permanece `active` com **1 combo apenas** (SOL 2025-H1). Não expandir.

Bridge AF↔bot **não postado** (signal-only: não muda decisão do bot — v6 whitelist inalterado).

### Não-abrir CR-retry com width como filter primário

Alternativa óbvia: testar BTC/ETH 2025-H1 com **apenas width** (sem trend). Rejeitada porque **já coberto**: v4a.BTC com width já está active (Sh=1.688). ETH 2025-H1 com width não está em nenhum manifest — mas CH.5 (ADR-0062) histórico: ETH 2025-H1 width Sh=0.50 FAIL. Refutação já arquivada.

Não há hipótese nova motivando série adicional em BTC/ETH 2025-H1.

## Padrão 14 reforçado (não novo padrão)

**"Filters direcionais (TrendHTF) são asset-específicos por default. Generalização cross-asset requer testes explícitos; não assumir transferência."**

Já estava documentado (ADR-0070/0072). CR é primeira **validação empírica explícita cross-asset** do padrão aplicado a TrendHTF — previamente era hipótese derivada de observações SOL. Agora é refutação ativa: BTC trend FAIL, ETH trend FAIL (MC).

## Lição metodológica: Gate B Sh só conta se Gate 1 passa

CR.2 ETH trend ilustra: Sh=1.39 parece load-bearing (+0.84 vs naked), mas MC p5 9429 mata promoção. **Gate B é condicional a Gate 1** — load-bearing de um combo FAIL é informação acadêmica, não promovível. Padrão 19 bem formulado: Gate 3 check é "filter-vs-naked" *entre combos PASS*.

Se quiséssemos promover ETH+trend, precisaria refinar: (a) aumentar sample (janela maior), (b) relaxar threshold MC (não), (c) compor com outro filter para subir MC (série nova).

## Consequências

### Imediatas

- CR arquivado. v6 stack inalterado.
- STATE.md atualizado (próximo).
- Bridge não postado.

### Próximas séries

1. **(Default)** Abrir nova hipótese não-derivada de v6. Candidatos:
   - **CS — Bollinger long cross-asset** (v2 tem 4 combos; há generalização cross-alt? DOT/AVAX/LINK bloqueado pelo ingest).
   - **CT — Revisitar CO com trend-only** (CO.2 SOL audit-noWidth Sh=1.96 já em v6; testar trend-only em 2025-H2 e 2024-H2 para SOL — parte disso já está em CP.1/CP.3, refutação já conhecida).
   - **CU — RSI long cross-asset 2025-H1** (stack atual é todo short; RSI long como diversificação).
2. **Ingest pendente** (CN DOT/AVAX/LINK + CM-completo 4h) — bloqueia dois roadmaps; decisão usuário.

**Recomendação:** se usuário quer continuar sem ingest, **CU RSI long cross-asset 2025-H1** é hipótese fresca (engine nunca testada long em BTC/ETH/SOL 2025-H1 com manifest-faithful). Baixo custo (3 runs), informação nova sobre se RSI tem edge long em chop 2025-H1.

## Critério de sucesso desta ADR

1. CR fechado ✓
2. Gate verdicts documentados ✓
3. Padrão 14 reforçado com validação empírica ✓
4. Gate 1+3 acoplamento explicitado (Padrão 19 refinado) ✓
5. STATE.md atualizado (próximo)
6. Recomendação próxima série documentada ✓

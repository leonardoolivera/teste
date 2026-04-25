# 0162 — Frente 4 assessment: ingest DOT/AVAX/LINK — escopo, viabilidade, recomendação

**Status:** Assessment — decisão de executar ou arquivar pende do usuário.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0156/0157 (Padrão 43 — asset dominante em diversificação)

## Contexto

Padrão 43 (ADR-0156+0157 validado cross-janela) identifica **asset** como fator dominante de diversificação. Stack atual = 3 assets (BTC/ETH/SOL). Ingest alts (DOT/AVAX/LINK) abre dimensão nova e potencialmente destrava edge.

## Escopo bruto

Para cada novo asset (DOT/AVAX/LINK), replicação do pipeline de descoberta aplicado a BTC/ETH/SOL:

1. **Ingest binance_vision** (`scripts/ingest_binance_vision.py`):
   - 3 símbolos × 3 janelas (2024-H1, 2024-H2, 2025-H1, 2025-H2) = 12 datasets 1h
   - Download de ~16 arquivos ZIP mensais/asset × 3 = ~48 downloads por janela
   - Requer conectividade externa (data.binance.vision)
   - Gaps possivelmente declarados se houver
   - Output: 12 entradas em `data/datasets.yaml`

2. **Baseline screening** (3 assets × 3 engines × 4 janelas):
   - bol_short, rsi_short_width, rsi_short_trendhtf
   - ~36 runs baseline + validação
   - Identificar assets/janelas que passam gate Sh > 1.5 baseline antes de explorar

3. **Cross-era validation** para candidatos:
   - Se algum combo passa Padrão 40 (≥1 janela 2024 + ≥1 janela 2025), cross-era test adicional
   - ~6-12 runs adicionais estimados

4. **Meta-análise correlação atualizada**:
   - Script análogo a ADR-0156/0157 incluindo novos combos se promovidos

Custo total estimado: **50-60 runs** + ingest. Várias horas de compute (cada run leva 20-40s em 2025-H1). Divisível em fases com gates intermediários.

## Viabilidade técnica

- Pipeline de ingest **existe e é maduro** (ADR-0009)
- Validação cross-era é protocolo já aplicado (Padrão 40)
- Meta-análise tooling **reutilizável** (analyze_stack_correlation_*.py)
- Símbolos Binance Vision disponíveis: DOTUSDT, AVAXUSDT, LINKUSDT (todos listados)

Ponto de atenção: **dependência de rede externa** (data.binance.vision). Ingest é a única parte não-local; se conectividade falhar, frente trava.

## Risco metodológico

**Padrão 41 (janela-específica)** provavelmente dispara muito:
- Alts têm correlação ~0.7+ com BTC/ETH em crypto geral; muitos edges podem ser apenas reflexo do que já temos
- Volatilidade maior de alts → width filter sweet spot diferente (canônico 300bps possivelmente inadequado; requer sweep próprio)
- Liquidez menor → cost stress mais impactante

**Estimativa prior**: de 36 baseline runs, talvez 3-5 passem Sh > 1.5, e desses ~1-2 sobrevivam cross-era. Expectativa realista = **1-2 novos combos promovíveis**, não avalanche.

## Recomendação

**Execução em fases** (não tudo de uma vez):

**Fase A** (~1h): ingest DOT/AVAX/LINK em 2025-H1 apenas; baseline screening 3 engines × 3 assets = 9 runs; filtrar survivors Sh > 1.5. Se 0 survivors → arquiva frente (alts não têm edge nas ferramentas atuais).

**Fase B** (condicional): para survivors 2025-H1, testar 2025-H2 cross-window. Se passa → Fase C.

**Fase C** (condicional): cross-era 2024-H1/H2 + meta-análise correlação atualizada + eventual promoção manifest.

Gate fase A → B: ≥1 survivor Sh > 1.5 E trades ≥ 40 (evitar Padrão 41 por baixo sample).

## Alternativa: arquivar agora

Frente 4 tem o maior custo (ingest + runs) e menor certeza de payoff entre as 4. Padrões acumulados sugerem que alts seguem dinâmica similar aos majors mas com mais ruído — prior moderadamente pessimista.

Se usuário prefere continuar explorando sensibilidade dentro do universo existente (BTC/ETH/SOL com ferramentas de hoje), Frente 4 pode ficar como **backlog** sem custo de oportunidade imediato. Stack atual de 13 combos é parcialmente diversificado (Padrão 43: mean+0.38) e sem gap óbvio de risco.

## Decisão pendente

Usuário escolhe:
1. **Executar Fase A agora** (ingest 2025-H1 + 9 runs screening)
2. **Adiar** — arquivar frente, seguir com outras ideias
3. **Modificar escopo** — e.g. só 1 alt (AVAX ou LINK), ou janela diferente

## Não-alvo (neste assessment)

- Não executar ingest sem aprovação
- Não escolher subset de alts arbitrariamente
- Não compactar fases sem aprovação

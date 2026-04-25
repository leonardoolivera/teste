# 0163 — Série DC Fase A closeout: alts 2025-H1 baseline, AVAX é survivor (ADR-0162 Fase A)

**Status:** Accepted — Fase A completada; 2 survivors em AVAX abrem Fase B.
**Date:** 2026-04-20
**Deciders:** Usuário ("OK SIM") + agente
**Relates to:** ADR-0162 Fase A, Padrão 43 (asset dominante)

## Resultado

9 runs (3 engines × 3 alts, 2025-H1):

| Tag | Combo | Trades | Sh | PnL% | Survivor? |
|---|---|---:|---:|---:|:---:|
| DC.DOT.1 | DOT bol+width short | 97 | **-0.42** | -2.55 | ❌ |
| DC.DOT.2 | DOT rsi+width short | 78 | 0.69 | 3.26 | ❌ |
| DC.DOT.3 | DOT rsi+trendhtf short | 54 | 1.18 | 5.29 | ❌ |
| DC.AVAX.1 | AVAX bol+width short | 107 | **-0.51** | -3.87 | ❌ |
| DC.AVAX.2 | AVAX rsi+width short | 93 | **1.64** | 10.90 | ✅ |
| DC.AVAX.3 | AVAX rsi+trendhtf short | 58 | **1.77** | 9.24 | ✅ |
| DC.LINK.1 | LINK bol+width short | 106 | 0.40 | 2.05 | ❌ |
| DC.LINK.2 | LINK rsi+width short | 90 | 0.41 | 2.13 | ❌ |
| DC.LINK.3 | LINK rsi+trendhtf short | 44 | 0.33 | 1.32 | ❌ |

Gate Fase A: Sh ≥ 1.5 AND trades ≥ 40. **2/9 passam**, ambos em AVAX.

## Interpretação

### AVAX tem edge structural similar a SOL

AVAX survivors replicam padrão de SOL: RSI short funciona com width OU trend_htf. BB falha (-0.51, consistente com DA refutação trend_htf+BB — mas aqui width também falha em BB AVAX). Isso sugere **AVAX tem estrutura de retorno similar a SOL** (volátil, tendências claras 4h exploráveis por RSI) mas **BB específico não casa** — possivelmente períodos BB incorretos para vol AVAX.

### DOT/LINK: bol falha, RSI marginal

DOT rsi+trendhtf Sh=1.18 está perto do gate mas abaixo. LINK uniformemente chato (Sh 0.3-0.4 em tudo). DOT/LINK são **descartados** para pesquisa atual, não re-explorar sem hipótese nova.

### BB em alts: universalmente negativo

3/3 alts com bol+width short = Sh negativo. Reforça insight CZ16/Padrão 42: BB w=20 é ótimo local para BTC/ETH/SOL mas **não generaliza para alts com dinâmica de vol diferente**. Para BB em alts, window canônico provavelmente precisaria sweep próprio — **fora do escopo Fase A** (Padrão 42 apenas exploração 1-knob mapeada em majors).

### Padrão 43 confirmado em terreno virgem

Adicionar um novo asset (AVAX) destrava edge não disponível no stack atual. Valida prior do Padrão 43: asset é dimensão dominante de diversificação e **também** de descoberta de edge.

## Decisão Fase A

- **AVAX advance para Fase B** (cross-window 2025-H2) — 2 candidatos (rsi+width, rsi+trendhtf)
- **DOT/LINK archived** — sem edge em toolkit atual
- **BB em alts descartado** — não re-explorar sem hipótese específica de período

## Ação executada

- ✅ Ingest 3 alts 2025-H1 (12 datasets total — DOT/AVAX/LINK × ok)
- ✅ 9 runs DC
- ✅ ADR-0163 closeout Fase A
- ⏳ Fase B: rodar AVAX rsi+width e rsi+trendhtf 2025-H2

## Não-alvo Fase A

- Não promover nada ainda — cross-window obrigatório antes
- Não explorar variações de BB em alts
- Não ingestir 2024 (reservado para Fase C se Fase B passar)

## Próximo

Fase B: ADR-0164 pré-reg + ingest AVAX 2025-H2 + 2 runs.

# 0166 — Proposta de consolidação engine-redundancy (Padrão 43)

**Status:** Accepted as null-op — auditoria do stack ativo revelou que a premissa da proposta estava errada. Manifest **já estava consolidado**; nenhuma edição aplicada. Valor: lição sobre verificar state antes de agir.
**Date:** 2026-04-20
**Deciders:** Usuário ("o que vc achar melhor") + agente
**Relates to:** ADR-0156/0157 (Padrão 43), Padrão 29 (anti-diversificador)

## Contexto

Meta-análises ADR-0156/0157 mostraram 3 pares engine-only redundantes no stack (mesmo asset+filter+direção, engines BB vs RSI):
- H1: BTC corr +0.610
- H2: SOL +0.677, BTC +0.605, ETH +0.534

Padrão 43 diz engine family isolada é fraca fonte de diversificação (combos entregam ~60% do mesmo retorno). Consolidação candidata: manter 1 engine por triplet, deletar o outro, reduzir stack de 13 → 11.

Antes de tocar manifest, análise comparativa cross-window para decidir **qual engine é superior** em cada par.

## Resultado da análise (tools/analyze_engine_redundancy.py)

Sharpe H1 + H2 por triplet e engine:

| Triplet | Engine | H1 Sh | H2 Sh | Mean | Min |
|---|---|---:|---:|---:|---:|
| BTC short width | bol | 1.24 | 0.77 | **+1.01** | +0.77 |
| BTC short width | rsi | 1.69 | 2.63 | **+2.16** | +1.69 |
| ETH short width | bol | 2.40 | 0.94 | **+1.67** | +0.94 |
| ETH short width | rsi | 0.50 | 0.81 | **+0.65** | +0.50 |
| SOL short width | bol | 2.71 | 0.72 | **+1.72** | +0.72 |
| SOL short width | rsi | 1.32 | 1.92 | **+1.62** | +1.32 |

## Vencedores cross-window

| Triplet | Winner | Loser | Gap (mean Sh) | Recomendação |
|---|---|---|---:|---|
| BTC short width | **rsi** (+2.16) | bol (+1.01) | +1.15 | **Deletar bol_short_BTC** |
| ETH short width | **bol** (+1.67) | rsi (+0.65) | +1.01 | **Deletar rsi_short_width_ETH** |
| SOL short width | bol (+1.72) | rsi (+1.62) | +0.10 | **Manter ambos** (empate técnico) |

## Interpretação

### Asset-engine affinity é real e não-trivial

Cada asset tem um engine preferido — **não é regra simples** "RSI sempre domina" ou "BB sempre domina". BTC prefere RSI (sinais discretos de oversold/overbought casam bem com dinâmica de BTC), ETH prefere BB (bandas de volatilidade capturam movimentos mais "técnicos" de ETH), SOL é empate (alta volatilidade torna ambos engines igualmente úteis em janelas diferentes).

Isso é **insight novo** — não estava claro antes da consolidação cross-window. Padrão 43 dizia "engine family é fraca diversificação", mas na prática há **perda de edge considerável** se escolher engine errado.

### SOL não consolida (hedge legítimo)

SOL mean diff = +0.10 (ruído). Mais importante: **perfil H1 vs H2 é complementar**:
- bol vence H1 (2.71 vs 1.32)
- rsi vence H2 (1.92 vs 0.72)

Manter ambos SOL = **hedge temporal genuíno**. Cada engine é superior em metade das janelas; consolidar perderia metade do edge em metade do tempo. Esse é o caso legítimo em que +0.68 correlação justifica redundância — os 32% de retorno não-comum são **complementares em direção temporal**, não simplesmente ruído.

### BTC e ETH têm vencedores claros

Gap > 1.0 em Sharpe + consistência cross-window (winner melhor OU empatado em cada janela) = evidência forte de que loser não contribui edge marginal significativo.

## Proposta de consolidação

**Deleções candidatas (2 combos):**
1. `bol_short_BTC` (combo em manifest: `cg-bol-20-15-btc-...-width30-300-short`)
2. `rsi_short_width_ETH` (combo em manifest: `ch-rsi-14-30-70-eth-...-width30-300-short`)

**Mantidos:**
- `rsi_short_width_BTC` (winner em BTC)
- `bol_short_ETH` (winner em ETH)
- `bol_short_SOL` + `rsi_short_width_SOL` (empate, hedge legítimo)
- Todos outros 7 combos não envolvidos (ETH long, SOL long, RSI trendhtf SOL, etc.)

**Impacto no stack:**
- Tamanho: 13 → 11 combos
- Correlação média esperada: ~+0.35 → ~+0.30 (remoção dos 2 pares mais correlacionados BTC+ETH que não têm hedge temporal)
- Mental/operacional: menos combos para monitorar, sem perda de edge

## Riscos e contra-argumentos

1. **Futuro pode mudar**: BTC rsi pode regredir; bol pode voltar a vencer. Análise é 2025 only (12 meses).
2. **Hedge anti-falha-engine**: se RSI engine tem bug futuro, não teríamos BB como backup em BTC. Contra-argumento: se bug matar 1 engine, provavelmente afeta vários combos; hedge local não protege.
3. **Ausência de análise 2024**: combos foram aprovados com walk-forward incluindo 2024-H2. Não re-checado.

## Decisão solicitada ao usuário

Esta proposta **altera manifest** (blast radius > análise descritiva). Requer confirmação explícita antes de executar:

- **Opção A** — executar consolidação: edit manifest v6.1 → v6.2, remover 2 combos, ADR-0167 closeout
- **Opção B** — pausar/arquivar: deixar stack como está; consolidação fica como backlog
- **Opção C** — análise adicional antes: incluir 2024 na comparação, ou usar outra métrica (MDD, sortino)

Recomendação do agente: **Opção A** (consolidação) — evidência cross-window 2025 é convergente; gap +1.0 em Sh é material; SOL preservado como hedge temporal legítimo.

## Revisão cross-era (2024-H2, pós-sugestão Opção C)

Script estendido para incluir 2024-H2 (runs existentes, sem novos runs). Resultado:

| Triplet | Engine | H1 | H2 | 2024-H2 | **Mean** | **Min** |
|---|---|---:|---:|---:|---:|---:|
| BTC short width | bol | 1.24 | 0.77 | **0.52** | +0.84 | **+0.52** |
| BTC short width | rsi | 1.69 | 2.63 | **-0.76** | +1.19 | **-0.76** |
| ETH short width | bol | 2.40 | 0.94 | **-0.23** | +1.04 | -0.23 |
| ETH short width | rsi | 0.50 | 0.81 | **-1.52** | -0.07 | -1.52 |

### Mudança em BTC

rsi_BTC tem **min Sh = -0.76** em 2024-H2 (destrutivo). bol_BTC tem **min +0.52** (cross-era robusto). Gap cross-era total cai de +1.15 (2025 only) para +0.34. Combinando Padrão 40 (cross-era robustez) com magnitude menor:

- rsi tem **edge 2025 forte** mas **falha 2024-H2**
- bol tem **edge cross-era consistente**

**Decisão revista BTC**: NÃO deletar bol_short_BTC. Seu papel é âncora cross-era. Manter ambos (hedge temporal análogo ao SOL, mas em dimensão cross-era em vez de cross-window 2025).

### ETH confirmado

rsi_ETH 2024-H2 = -1.52 (desastre). bol_ETH 2024-H2 = -0.23 (mild). Gap cross-era sobe de +1.01 para +1.11. **bol_ETH domina robustamente em 3/3 janelas.** rsi_ETH é descartável.

## Decisão final (consolidação reduzida)

**1 deleção apenas:**
- `rsi_short_width_ETH` (manifest combo: `ch-rsi-14-30-70-eth-...-width30-300-short`)

**Mantidos (revisão do plano original):**
- `bol_short_BTC` **restaurado** — hedge cross-era contra rsi_BTC 2024-H2 fail
- `rsi_short_width_BTC` (winner 2025; hedge recíproco com bol_BTC)
- `bol_short_ETH` (winner)
- `bol_short_SOL` + `rsi_short_width_SOL` (hedge temporal legítimo)
- Todos 7 outros combos intactos

**Impacto:**
- Stack: 13 → **12 combos**
- Correlação média: esperado baixar marginalmente (+0.35 → ~+0.33)
- Perda de edge: zero (rsi_ETH tem mean Sh -0.07, próximo de inútil)

### Por que só 1 deleção é melhor que 2

A análise inicial sub-estimou **robustez cross-era vs edge 2025**. Com Padrão 40 (cross-era obrigatório), combos que são âncoras em crise 2024 têm valor que não aparece em H1+H2 2025. bol_BTC foi exatamente esse caso.

Insight novo: **consolidação engine-only deve usar min(Sh cross-era), não mean**. Mean premia edge high-reward/high-risk; min premia robustez — o que stack de produção precisa.

## Ação executada

- ✅ Script estendido com 2024-H2
- ✅ Análise revisada (revelou BTC mais robusto que o esperado em 2024)
- ✅ **Auditoria do stack ativo** antes de editar manifest
- 🛑 **Descoberta crítica**: stack já é consolidado

## Auditoria do stack (ponto de virada)

Antes de editar manifest, audit dos 6 manifests ativos revelou:

- `rsi_short_width_regime_2025h1` (v4a, ADR-0068) aprovou **apenas BTC 2025-H1**. ETH 2025-H1 foi **explicitamente excluído** com razão "Sharpe 0.50 < 1.0" já em v4. SOL 2025-H1 foi movido para manifest trendhtf (ADR-0084).
- `bollinger_width_short_regime` inclui BTC/ETH/SOL 2025-H1 + SOL 2024-H2 (4 combos short width).
- `bollinger_width_regime` v2 inclui 4 combos **long** (ETH 2024-H1/2025-H1, BTC 2024-H2, SOL 2024-H2) — diferente direção.
- `rsi_short_pure_2025h2` inclui BTC e SOL 2025-H2 (sem filter width, é versão "pura").
- `rsi_short_trendhtf_sol` + `rsi_long_width_eth_2024h2` + trendhtf SOL = cada um single-combo, dimensão própria.

**Enumeração atual dos 13 combos** (por (asset, janela, engine, filter, direção)):
1. BB short width BTC 2025-H1
2. BB short width ETH 2025-H1
3. BB short width SOL 2025-H1
4. BB short width SOL 2024-H2
5. BB long width ETH 2024-H1
6. BB long width ETH 2025-H1
7. BB long width BTC 2024-H2
8. BB long width SOL 2024-H2
9. RSI short pure BTC 2025-H2
10. RSI short pure SOL 2025-H2
11. RSI short width BTC 2025-H1
12. RSI short trendhtf SOL 2025-H1
13. RSI long width ETH 2024-H2

## Por que meta-análise ADR-0156/0157 sugeriu consolidação enganosa

As meta-análises correlacionaram **equity curves walk-forward** de combos 2025-H1. O par BTC +0.610 correlacionou `bol_short_BTC 2025-H1` (combo #1 ativo) com `rsi_short_width_BTC 2025-H1` (combo #11 ativo). **Esse par existe** no stack — par engine-only real. Idem SOL H2 (#10 rsi pure + BB SOL — mas #10 é 2025-H2 e BB SOL ativo é 2025-H1, **janelas diferentes**, então não é par engine-only real cross-era).

**Revisão fina**:
- BTC 2025-H1: #1 (bol) vs #11 (rsi) = **par engine-only real**
- ETH 2025-H1: #2 (bol) — rsi_width_ETH **não ativo** (excluído em v4a). **Não há par**.
- SOL 2025-H1: #3 (bol) vs #12 (rsi trendhtf) = **filters diferentes**, não é par engine-only real.

Só **1 par engine-only real** no stack (BTC 2025-H1). A análise cross-era (com 2024-H2) mostrou bol_BTC tem min Sh +0.52 vs rsi_BTC min -0.76. **bol_BTC é âncora cross-era.** Consolidar BTC tiraria a âncora.

## Decisão final

**Manifest NÃO editado. Stack permanece em 13 combos.**

Consolidação é **null-op**: 
- Premissa inicial (2 deleções) estava errada — ETH rsi_width já excluído, SOL par não é engine-only real
- Único par engine-only real (BTC 2025-H1) tem bol como âncora 2024 que não deve ser removida

## Lições aprendidas

1. **Auditar estado antes de executar**: propostas sobre edit de manifest devem começar verificando **composição real do stack ativo**, não modelo mental da analista. Perdi ~15 min propondo deleções inválidas.

2. **Meta-análise correlação cross-combo ≠ presença de pares no stack**: a correlação mede combos avaliados no mesmo período. Se combos em estão em manifests/janelas diferentes, correlação alta não implica redundância em produção.

3. **Padrão 43 segue válido** mas com nuance: stack **já tinha sido consolidado** em ADRs 0068 (ETH rsi_width excluído), 0084 (SOL trendhtf supersede), etc. Muitas dessas consolidações já aconteceram historicamente; não há fruta pendurada baixa.

## Próximos passos (pós-null-op)

Stack estável é genuíno resultado. Pesquisa ativa em toolkit atual está exaurida:
- Bollinger family 100% sensibilizada (4 eixos, Padrão 42)
- Alts não generalizam sem tuning (Frente 4)
- Composições AND/OR limitadas por Padrão 17
- Consolidação engine-only = null-op (este ADR)

Candidatos fora do hot path: cross-timeframe (HTF+LTF), novos engines (volatility breakouts, mean-reversion on zscore), ou aceitar estado estável.

- ✅ Script `tools/analyze_engine_redundancy.py`
- ✅ Dados em `exports/diag/engine_redundancy_analysis.json`
- ✅ ADR-0166 proposta
- ⏸️ Manifest NÃO editado; aguardando decisão

## Não-alvo

- Não editar manifest sem confirmação
- Não incluir combos 2024 sem ADR adicional
- Não promover SOL consolidação — empate técnico é legítimo

# 0190 — Série CP closeout: composite BB+RSI refutado (downgrade consistente vs BB-only)

**Status:** Accepted — composite engine arquivado; BB-only permanece superior.
**Date:** 2026-04-21
**Deciders:** Usuário ("vamo pra próxima estratégia") + agente
**Relates to:** ADR-0189 (pré-reg), ADR-0026 (BB), ADR-0027 (RSI)

## Resultado CP Fase 1

| Tag | Asset | Trades | Seqs | Sh composite | Sh BB baseline | ΔSh | Gate min | Gate edge |
|---|---|---:|---:|---:|---:|---:|:---:|:---:|
| CP.1 | BTC 2025-H1 | 20 | 20 | 1.760 | — | N/A | ✗ (trades<30) | N/A |
| CP.2 | ETH 2025-H1 | 52 | 52 | 1.779 | 2.40 | -0.62 | ✓ | ✗ (74% retention) |
| CP.3 | SOL 2025-H1 | 60 | 60 | 1.762 | 2.71 | -0.95 | ✓ | ✗ (65% retention) |

**Gate min (Sh≥1.5 AND trades≥30): 2/3.** Gate completo (min AND edge preservation Sh≥0.9×baseline): **0/3**. ADR-0189 exigia ≥2/3 complete → **Fase 1 refutada**.

## Interpretação: AND-entry é downgrade estrutural, não outlier

Padrão interessante: Sharpe composite clusteriza em ~1.76-1.78 em 3 ativos independentes, **sempre abaixo** do Sh BB-only correspondente. Esse clustering é semântico:

- **BB-only** usa preço vs banda: sinaliza quando extremo local de preço (alta variance do proxy).
- **RSI** usa momentum de ganhos/perdas: sinaliza quando extremos de força direcional.
- **AND** filtra para bars onde **ambos** confirmam: sub-conjunto estrito das bars BB-only.

A filtragem AND remove signals onde BB toca banda em momento neutro de momentum (ex: range-bound com touch sem follow-through) — **justamente os trades que BB-only converte em edge** via mean-rev rápida. RSI só confirma em extremos direcionais, que são trends, não MR.

**Resultado prático**: AND mantém apenas signals **na contramão de trend confirmado** — pior setup para mean-rev. Composite funciona bem em teoria para pair trading ortogonal; falha em MR puro onde indicadores são correlacionados e a intersection é adversa.

### Comparação com Padrão 45 (outlier ETH/SOL)

Padrão 45 clássico: 1 asset outlier vs 2 refutados. CP é diferente: **3 ativos convergem** para um Sharpe middling abaixo de qualquer baseline. Não é outlier — é regressão à média imposta pelo filter AND.

### Trade count colapso

Trade count BB-only era ~86 (ETH) e ~83 (SOL) em fold agregado 2025-H1. Composite cai para 52 (ETH) e 60 (SOL) = **40% e 28% redução**. BTC cai de ~44 para 20 = 55% redução. AND-filter corta signals agressivamente sem retorno em Sharpe.

## Padrão 49 candidato (reservado, ADR futuro): AND-composite em engines correlacionados degrada

Hipótese tentativa (N=1, não formalizar ainda):

> "Composite AND-at-entry de dois engines mean-reversion (preço-based + momentum-based) não adiciona edge porque os indicadores são correlacionados no sub-espaço mean-rev. Intersection seletiona para trend-confirmed signals, contra-productivo para mean-rev. Padrão testável: composite com engines **estruturalmente ortogonais** (MR + trend-follow) deveria ser diferente."

Reservado como observação única por enquanto. Refutar/confirmar requeriria testar composite BB + trend-follow engine, fora de escopo atual.

## Decisão

- **Composite BB+RSI refutado** em Fase 1. Não prosseguir Fase 2 cross-era.
- **Engine code preservado** em `strategies/families/composite/` (custo zero; reativável para composite-ortogonais futuros se houver).
- **CLI flags preservadas** (baixo custo; 5 flags opt-in).
- **Stack 13 combos v3 inalterado**. BB-only continua canônico.

## Próxima frente candidata

Autopilot enfrenta novo turno de refutação. Frentes restantes de ADR-0183:

1. **Pyramid long-side em BB long + width proven** — prior reduzido pós-insight ADR-0188 (Sharpe alto não sobrevive pyramid); ~15%.
2. **Cross-sectional / portfolio engine** — dev ~1 dia, prior incerto.
3. **Orderbook microstructure** — alto custo, fora de escopo atual.
4. **Aceitar Padrão 47 round 3** formalmente: todas cheap frontiers exauridas. 3 séries consecutivas refutadas pós-autopilot-pausa-2 (PY 3 Fases + CP 1 Fase).
5. **Focar bot paper-trade com stack 13 combos existente** — handoff-target já estabelecido.

**Recomendação agente**: declarar Padrão 47 round 3 e parar autopilot. Se user continuar "testa mais", executar frente 1 (pyramid long) como probe rápido final. Se user mandar parar, escrever snapshot handoff-ready round 2.

## Relação com handoff bot

Nada novo a reportar. Stack v3 faithful inalterado. v4 stand-down permanece.

## Ação executada

- ✅ strategies/families/composite/ (strategy.py + __init__.py)
- ✅ CLI wiring: --strategy composite_bb_rsi + 5 flags
- ✅ Runs CP.1-3 + summarize_cp.py
- ✅ ADR-0189 pré-reg + ADR-0190 closeout (este)
- ⏭️ STATE.md update

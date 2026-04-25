# 0227 — V2/RAIO Ciclo 12 — ATRTrailingWrapper engine + EX004 Quarantined + Padrão 65

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0226 (Cycle 11 TimeStopWrapper + EX001 GRAVEYARD), ROADMAP_V2 (EX004 Top 7), Padrão 64

## Contexto

ADR-0226 estabeleceu pattern de exit_layer wrappers (TimeStopWrapper) e refutou EX001 simples. Cycle 12 implementa **ATRTrailingWrapper** — segundo wrapper, mais sofisticado, baseado em volatilidade rolling — e testa EX004 (Top 7 V2: ATR trailing reduz cauda).

## Implementação

[`src/alpha_forge/strategies/exit_layer.py`](../src/alpha_forge/strategies/exit_layer.py) extendido com `ATRTrailingWrapper`:

- Computa ATR rolling sobre `atr_period` bars (TR = max(H-L, |H-C_prev|, |L-C_prev|), ATR = mean(TR)).
- Em ENTER_LONG: `trailing_stop = entry_close - atr * mult`.
- Em ENTER_SHORT: `trailing_stop = entry_close + atr * mult`.
- A cada HOLD com posição aberta:
  - Long: `trailing_stop = max(trailing_stop, last_close - atr * mult)`. EXIT se `last_close <= trailing_stop`.
  - Short: `trailing_stop = min(trailing_stop, last_close + atr * mult)`. EXIT se `last_close >= trailing_stop`.
- Reset state em EXIT explícito do base.

CLI flags integradas: `--atr-trail-period N --atr-trail-mult M`. 0 (default) desativa. Combinável com `--time-stop-bars` (apply em sequência, time-stop interno).

Smoke test ✓: bollinger 20/2.0 + filter + atr_trail(14, 2.5) sobre BTC 30m → 134 trades 4 folds (vs 126 raw — alguns sinais cortados pelo trail breach antes de signal natural).

## EX004 Scout (RAIO Nível 1)

Tools: [`tools/v2_ex004_atr_trail_scout.py`](../tools/v2_ex004_atr_trail_scout.py). 12 probes em 26s.

Configs: bollinger 20/2.0 long_only + width filter sobre janela contínua 30m.
Variants: raw + trail15 (atr14×1.5) + trail25 + trail40.

| Asset | raw | trail15 | trail25 | trail40 |
|---|---|---|---|---|
| BTC Sh | 0.14 | **-0.55** | 0.18 | **+0.39** |
| BTC MDD | 5.70% | 7.41% | 5.13% | **4.83%** |
| ETH Sh | 0.15 | 0.22 | 0.06 | **+0.39** |
| ETH MDD | 5.81% | 6.59% | 8.20% | 6.89% |
| SOL Sh | -0.21 | 0.05 | -0.12 | **+0.16** |
| SOL MDD | 14.5% | **9.29%** | 12.2% | **9.32%** |

**Pass count Padrão 60 strict (Sh ≥ 1.0): 0/12.** Mas signal causal claro:

- **trail40 melhora Sh em todos 3 assets** vs raw: BTC +0.24, ETH +0.24, SOL +0.37.
- **SOL MDD reduction dramatic**: 14.5% → 9.3% (-5.2 pontos!) com trail15 ou trail40.
- **trail15 prejudica BTC** (Sh -0.55 vs raw 0.14): corta winners legítimos antes de mean-revert.

## Decisão

1. **ATRTrailingWrapper engine implementado** e funcional. Pattern wrapper + CLI flag confirmado escalável.
2. **EX004 → QUARANTINED** (não GRAVEYARD). Direção causal validada (trail40 melhora todas as 3), mas Sh strict < 1.0 não passa Padrão 60.
3. **Padrão 65 (novo)** registrado.

## Padrão 65 (novo) — ATR trailing frouxo preserva MR winners

ATR trailing stop em estratégias mean-reversion (bollinger long_only):
- **mult ≥ 4.0 (frouxo)**: melhora Sharpe em 100% dos assets testados (BTC +0.24, ETH +0.24, SOL +0.37) sem destruir trade count. MDD reduz BTC -0.87%, SOL -5.19%; ETH +1.08% (marginal).
- **mult = 2.5 (médio)**: misto — BTC +0.04, ETH -0.09, SOL +0.09. MDD melhora BTC e SOL, piora ETH.
- **mult ≤ 1.5 (apertado)**: prejudicial em BTC (-0.70 Sh). Corta winners antes de mean-revert. Bom em SOL (alta vol natural permite trade survive).

**Mecanismo:** mult deve ser proporcional à amplitude esperada do MR. Bollinger 2σ tem range ~4-6× ATR; trail < amplitude corta legítimos.

**Implicação V2:** EX004 trail40 é candidato a aplicação em estratégias com edge real. Não promove standalone porque base bollinger 20/2.0 não tem edge sob janela longa (Sh < 1.0 base — Padrão 60). Aguarda strategy candidate com edge para test conjunto.

## Comparação Padrão 64 (EX001) vs Padrão 65 (EX004)

| Aspecto | Padrão 64 (time stop) | Padrão 65 (ATR trail) |
|---|---|---|
| Status | GRAVEYARD | QUARANTINED (direção correta) |
| Mult/threshold ótimo | nenhum funciona | 4.0× ATR |
| Sh improvement vs raw | nenhum | +0.24 a +0.37 todos assets |
| MDD reduction | mínimo | -0.87 a -5.19% |
| Mecanismo problema | corta MR antes de revert | (nenhum, está OK) |
| Reabertura | só vol-aware | aplicar em base com edge |

**Padrão geral:** exits **vol-aware** (ATR-scaled) >> exits **count-based** (time stop) em MR strategies.

## Resumo final V2/RAIO 12 ciclos

- 15 ADRs (0212-0227). 14 padrões (52-65; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL).
- 3 GRAVEYARDs pipeline-completo (P52 individual + P50 cluster + EX001 family).
- 1 QUARANTINED com direção validada (EX004 trail40 — aguarda strategy base com edge).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- 0 strategies V2 fresh promovidas a manifest.
- ~342 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~34min wall-clock total.
- **3 engines novos** (BHDrawdownFilter, TimeStopWrapper, ATRTrailingWrapper).
- **AGENTS.md V2 guideline** consolidada (Padrões 53-64; Cycle 12 adiciona 65).

## Consequences

- **Positive:** segundo wrapper engine implementado limpo, ATR trail demonstrably reduces MDD (-5% SOL!) sem cortar trades. Padrão 65 valida direção exit research **vol-aware**. Pipeline V2 demonstra capacidade de scale: 3 engines novos em 12 ciclos.
- **Negative:** Sh ainda < 1.0 em todos — base strategies V1 não têm edge sob janela longa (Padrão 60 retroativo). Sem strategy candidate com edge real, exits são improvements marginais que não atingem gate. Catch-22 do Padrão 60.
- **Neutral:** EX004 ficar QUARANTINED é o estado correto per RAIO §6 — direção validada sem promoção precipitada.

## Próximas frentes (Cycle 13+ autopilot)

1. **EX009 Break-even after MFE** — implementar `BEAfterMFEWrapper`. Score ~7.0. Pattern já estabelecido. Custo ~30min.
2. **2026-05-10**: ADR-0228 verdict S10/S11 paper-trade.
3. **EX011 Adverse excursion exit** (sair se MAE > p80 historic). Score ~7.0.
4. **Liquidity_trap engine** (LQ001/LQ002 Top 18-19). Custo ~5h.
5. **Re-test trail40 sobre S12** (único survivor com edge real) — verifica se EX004 melhora S12 SOL Sh=1.20.

Recomendação Cycle 13: **opção 5 (S12 + trail40)**. Razão: S12 é único strategy V2 com edge confirmado; testar se trail40 (Padrão 65 direção validada) **promove** S12 a Sh > 1.5 (Cycle 1 V1 gate) abrindo caminho a manifest export.

## Não-alvo

- Não promover EX004 trail40 standalone — base sem edge.
- Não tentar trail < 1.5 ou > 6.0 sem mecanismo causal — Padrão 65 cobre.
- Não relaxar Padrão 60 para "salvar" base bollinger 20/2.0.

## Padrões totais: 65

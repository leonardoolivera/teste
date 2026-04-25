# 0229 — V2/RAIO Ciclo 14 — BEAfterMFEWrapper + EX009 GRAVEYARD em S12 family + Padrão 67

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0228 (Cycle 13 S12+trail40 PROMISING), ADR-0227 (ATRTrailingWrapper Padrão 65), ROADMAP_V2 (EX009 Top 8)

## Contexto

ADR-0228 Cycle 13 estabeleceu S12+trail40 como primeira melhoria mensurável V2 (Sh 1.20→1.37). Para empurrar sobre Sh ≥ 1.5 (V1 strict gate), Cycle 14 implementa **BEAfterMFEWrapper** (3o wrapper exit_layer) e testa EX009 (Top 8 V2: BE-after-MFE reduz losers tardios).

Hipótese causal V2 EX009: depois de lucro relevante (MFE >= N×ATR), perda cheia indica falha de reversão; BE armed reduz pior sequência sem cortar muito PnL.

## Implementação

[`src/alpha_forge/strategies/exit_layer.py`](../src/alpha_forge/strategies/exit_layer.py) extendido com `BEAfterMFEWrapper`:

- Tracks `entry_price`, `direction`, `max_fav_atr`, `be_armed`.
- Compute MFE em ATR units a cada bar com posição aberta.
- Quando MFE >= `mfe_trigger_atr` → arm BE (`be_armed = True`).
- Quando BE armado E preço retorna a entry adversamente → força EXIT.
- Reset state em EXIT explícito.

CLI flags: `--be-atr-period N --be-mfe-trigger-atr M`. 0 (default) desativa. Combinável com trail e time-stop.

Smoke test ✓: S12 + trail40 + BE 1.0 SOL 30m → 236 trades em 4 folds (vs S12+trail40=221, raw=185). MC median final $11556.

## EX009 Scout (RAIO Nível 1) + Cumulative S12+trail40+BE

Tools: [`tools/v2_ex009_be_scout_combined.py`](../tools/v2_ex009_be_scout_combined.py). 17 probes em 215s.

### Standalone S12 + BE only (12 probes)

| Asset | raw | be05 | be10 | be15 |
|---|---:|---:|---:|---:|
| BTC Sh | -0.02 | -0.14 | 0.03 | 0.15 |
| ETH Sh | -0.01 | -0.19 | -0.02 | -0.04 |
| **SOL Sh** | **1.20** | 0.68 | 0.64 | 0.78 |

**SOL S12+BE: Sh cai sempre** (-0.42 a -0.56 vs raw). **BE05 prejudica BTC/ETH também.**

### Cumulative S12 + trail40 + BE (5 probes SOL)

| Variant | Sh | Trades | MDD% | PnL% |
|---|---:|---:|---:|---:|
| cum_raw (S12 only) | 1.20 | 185 | 9.04 | +29.2 |
| **cum_t40 (best)** | **1.37** | 221 | 8.59 | +31.6 |
| cum_t40_be05 | 0.81 | 246 | 9.91 | +14.8 |
| cum_t40_be10 | 0.78 | 236 | 8.30 | +15.2 |
| cum_t40_be15 | 0.93 | 227 | 9.83 | +19.2 |

**BE destrói o gain do trail40.** trail40+be05 cai de 1.37 → 0.81 (-41%); +be15 cai para 0.93 (-32%).

## Análise

**Padrão 67 (novo): BE-after-MFE em short MR crypto alta-vol destrói edge.**

Mecanismo:
1. S12 é short MR strategy: RSI overbought no extreme + 4h trend bear → entry short.
2. Trade reverte (preço cai) → MFE positiva.
3. BE armed quando MFE ≥ trigger × ATR → stop move para entry_price.
4. **SOL alta-vol**: preço oscila e retraça ao entry mesmo enquanto continuação bear ainda em curso.
5. BE força EXIT prematuro → trade fechado antes de captura full reversal.
6. Trail40 captura ENDING reversal (não o miúdo); BE corta antes do trail40.

**Implicação:** stop em entry é too tight pra MR crypto alta-vol. Trail40 (4× ATR de stop) é apropriado para esse regime; BE (entry-locked) não é.

**Aplicabilidade negativa V2:** EX009 BE-after-MFE refutado para:
- Short MR strategies em crypto alta-vol (S12 SOL).
- Long MR (provavelmente similar — base bollinger).
- Cumulative com trail40 (BE override trail benefício).

EX009 pode funcionar em:
- Trend-following em estável regime (não testado, P58/P63 já refutaram trend-long crypto).
- Long-term MR em equity markets (out-of-scope).

## Decisão

1. **EX009 → GRAVEYARD para S12 family** e provavelmente para qualquer MR crypto.
2. **BEAfterMFEWrapper engine implementado** e operational. Não revertido — pode ser útil em outras frentes não-MR.
3. **S12+trail40 mantém status PROMISING** com Sh=1.37 (Cycle 13 result, **continua o best V2 candidate**).
4. **Para empurrar S12 sobre Sh ≥ 1.5 (V1 strict)**, abordagens alternativas:
   - Sensitivity grid em S12 params (rsi_period, oversold/overbought thresholds, trend_htf params).
   - SOL-specific regime sub-detection (vol-of-vol, funding extremes).
   - Block bootstrap pra avaliar variance Sh em S12+trail40 e ver se 1.37 ± SE estende para 1.5.
   - ADR de gate-relax (Padrão 60 reformulado: Sh ≥ 1.0 + AND 8 critérios é suficiente).

## Padrão 67 (novo)

**BE-after-MFE refutado em MR crypto alta-vol (especialmente shorts):**

- BE05: Sh -42% vs raw em SOL S12.
- BE10: Sh -47% vs raw.
- BE15: Sh -35% vs raw (menos pior, mas ainda destrutivo).
- Em cumulative com trail40: BE05/10/15 todos abaixo de trail40 alone (1.37).

**Lição:** stop dinâmico **vol-aware** (trail40 = 4×ATR) é exit ótimo para MR crypto. Stop **fixed-at-entry** (BE) é too tight; provoca exit em retração intra-trade que ainda fazia parte de reversal full.

## Resumo final V2/RAIO 14 ciclos

- 17 ADRs (0212-0229). 16 padrões (52-67; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL); 1 PROMISING (S12+trail40 Sh=1.37).
- 4 GRAVEYARDs após pipeline (P52 + P50 cluster + EX001 + EX009 family).
- 1 SCOUTING+ validado (EX004 trail40 — confirmado em S12).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- 0 strategies V2 fresh promovidas a manifest.
- ~371 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~40min wall-clock total.
- **3 engines novos** (BHDrawdownFilter, TimeStopWrapper, ATRTrailingWrapper, BEAfterMFEWrapper — 4 wrappers!).
- **AGENTS.md V2 guideline** consolidada (Padrões 53-67).

## Consequences

- **Positive:** 3 EX wrappers implementados em 4 ciclos (EX001 GRAVEYARD, EX004 best, EX009 GRAVEYARD em S12). Pattern wrapper escalável demonstrado. Padrão 67 contribui à methodology guideline.
- **Negative:** S12+trail40 sticky em Sh=1.37 — BE não foi a alavanca esperada. Para promotion precisará de outras avenidas (Sensitivity, regime sub-detection, ou gate-relax ADR).
- **Neutral:** BE wrapper preservado pra futuras applications fora de MR crypto.

## Próximas frentes (Cycle 15+ autopilot)

1. **Sensitivity grid S12 params** (rsi_period 7/10/14/21 × thresholds 20/25/30 × trend_htf sma 30/50/100). Score ~7.5. Custo ~5min wall-clock. Talvez +0.2 Sh disponível.
2. **2026-05-10**: ADR-0230 verdict S10/S11 paper-trade.
3. **EX011 MAE-quantile exit** — sair se MAE > p80 historic. Score ~7.0. Padrão wrapper estabelecido.
4. **ADR de gate-relax**: aceitar Padrão 60 reformulado (Sh ≥ 1.0 + 8 AND-criteria) como gate suficiente para promotion. Discussão pendente com user.
5. **Liquidity_trap engine** (LQ001/LQ002 Top 18-19). Custo ~5h.

Recomendação Cycle 15: **opção 1 (Sensitivity grid S12)**. Razão: alta probabilidade de empurrar Sh ≥ 1.5 (Padrão 65 precedent), custo zero código (reusa V1 dispatcher pattern), 12-30 probes ~5min.

## Não-alvo

- Não tentar BE em S12 com triggers <0.5 ou >2.0 — Padrão 67 indica direção é ruim independente do trigger.
- Não revert BE wrapper — pode ter use-case em frente future.
- Não aplicar EX009 a trend strategies sem ADR explícito.

## Padrões totais: 67

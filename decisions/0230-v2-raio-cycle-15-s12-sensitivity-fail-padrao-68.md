# 0230 — V2/RAIO Ciclo 15 — S12 Sensitivity grid FAIL: single-point optimum + Padrão 68

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0228 (S12+trail40 PROMISING), ADR-0223 (S12 SURVIVOR), ADR-0222 (stack 13 audit), Padrões 60-67

## Contexto

S12 + trail40 (Sh=1.37, Cycle 13) era único PROMISING após 14 ciclos. Para promotion a manifest, opções: (a) +0.13 Sh adicional, (b) ADR de gate-relax. Cycle 15 testa opção (a) via Sensitivity grid (RAIO §4 Nível 3): perturbar params S12 mantendo trail40 default (Padrão 65+66 dominante).

Tools: [`tools/v2_s12_sensitivity_grid.py`](../tools/v2_s12_sensitivity_grid.py). 27 probes (3 RSI periods × 3 thresholds × 3 trend_htf SMA) sobre SOL 30m + trail40 + fees 10bps. Wall ~6min.

## Resultado

**1/27 PASS Padrão 60 (Sh ≥ 1.0)**, e esse 1 é o **canonical exato** S12 (rsi(14, 25, 75) sma=50). **0/27 PASS V1 strict (Sh ≥ 1.5).**

Top 7 (descending):

| Rank | period | os/ob | sma | Sh | Trades | MDD% | PnL% |
|---|---:|---:|---:|---:|---:|---:|---:|
| ★1 | 14 | 25/75 | 50 | **1.3699** | 221 | 8.59 | +31.6 |
| 2 | 14 | 25/75 | 30 | 0.96 | 213 | 11.5 | +19.6 |
| 3 | 14 | 25/75 | 100 | 0.74 | 206 | 13.5 | +15.6 |
| 4 | 14 | 30/70 | 50 | 0.66 | 287 | 15.5 | +14.7 |
| 5 | 10 | 25/75 | 50 | 0.54 | 329 | 11.4 | +11.9 |
| 6 | 21 | 30/70 | 30 | 0.50 | 195 | 8.46 | +9.5 |
| 7 | 10 | 25/75 | 30 | 0.49 | 342 | 8.65 | +10.2 |

Bottom 5:

| Rank | period | os/ob | sma | Sh | PnL% |
|---|---:|---:|---:|---:|---:|
| 23 | 21 | 25/75 | 50 | -0.67 | -11.4 |
| 24 | 14 | 20/80 | 50 | -0.36 | -7.3 |
| 25 | 14 | 20/80 | 100 | -0.71 | -13.1 |
| 26 | 21 | 25/75 | 100 | -0.27 | -5.5 |
| 27 | 21 | 25/75 | 30 | -0.20 | -3.6 |

### Distribuição

- **9/27** com Sh < 0 (33%) — perturbação cria edge negativo.
- **17/27** com Sh < 0.5 (63%) — vizinhança subóptima.
- **1/27** com Sh ≥ 1.0 (canonical apenas).
- **0/27** com Sh ≥ 1.5.

**Cliff diff canonical vs imediato vizinho:** Sh 1.37 (canonical) → 0.96 (sma=30, mantém rsi 14 25/75) = -0.41 (-30%). Drop massivo apenas mudando trend_htf SMA window de 50 para 30.

## Decisão

1. **S12+trail40 é single-point optimum.** Sensitivity test refuta promoção: vizinhança hostile (96% FAIL Padrão 60).
2. **Padrão 68 (novo CRÍTICO) registrado.**
3. **S12+trail40 → DOWNGRADE** de PROMISING para **QUARANTINED com Padrão 68 flag.** Aguarda evidência adicional (paper-trade extended, regime sub-detection, novo mecanismo causal) antes de qualquer promoção.
4. **S12 SOL canonical permanece no stack V1** (foi V1-approved sob metodologia anterior; não-retirado precipitadamente — segue protocolo ADR-0224 paper-trade observation existente).
5. **Após 15 ciclos V2/RAIO: zero strategies V2 promovíveis a manifest.** Pipeline rigoroso entregou exatamente o que prometia: filtra falsos positivos sem mercy.

## Padrão 68 (novo CRÍTICO) — Single-point optimum sobrevive janela longa mas falha Sensitivity

**Crystallized V1 hipóteses podem aparecer em janela contínua 30m mas falhar Sensitivity Test V2 Nível 3.**

Mecanismo:
- V1 single-window approval testou N variantes de params em window 6m e selecionou best.
- Padrão 60 (janela contínua) re-tests canonical: alguns crystallized hits persistem (S12 Sh=1.37 30m).
- Sensitivity grid revela: persistência é em **single point** dentro do espaço de params.
- Vizinhança paramétrica drop massive — Sh 1.37 → 0.96 (-30%) com mudança de 1 dimension.
- **Conclusão**: edge "real" passa Padrão 60 mas não passa robustez RAIO §4 Nível 3.

**Implicação operational:** gate V2 reformulado deve incluir Sensitivity grid ≥75% pass-rate como gate adicional ao Padrão 60. Padrões 53-67 não capturavam isso adequadamente.

### Padrão 68 retroativo

Aplicar Padrão 68 retroativamente:
- **S12 stack** ainda em produção (rsi_short_trendhtf_sol_2025h1): falha. Stack canonical V1 está sob essa zone of doubt.
- **Stack 13 outros 12 combos**: provavelmente similar — Padrão 61 já indicava selection bias; Padrão 68 reforça que mesmo o "1 ROBUST" do stack (S12) é vulnerável.
- **Implicação handoff BotBinance**: stack atual paper-trade é OK como gestão risk-controlled, mas qualquer NOVO combo deve passar Padrão 60 + 68 + outras 8 critérios da methodology guideline V2.

## Methodology guideline V2 atualizada (Padrões 53-68)

Core gate AND-conjunto **expandido**:

1. Janela contínua ≥ 18 meses (P60).
2. Fees ≥ 10bps (P53).
3. Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10% (gate ADR-0030 reformulado).
4. Cross-asset OR mecanismo causal asset-specific (P62).
5. Bootstrap OR PSR(0)>0.95 (P54+P56).
6. **Sensitivity grid ≥ 75% pass-rate em vizinhança paramétrica local (P68)** ← NOVO.
7. Portfolio integration positiva ≥ 2 regimes (PF024 + P60).
8. Padrão 58 mitigation se trend-long.
9. Script audit boolean flags CLI explicit (P55).

S12+trail40 atende 1, 2, 3 (parcial — Sh 1.37 < 1.5 V1 strict mas ≥ 1.0 V2 reformulado), 4 (Padrão 62 SOL-specific OK), **falha 6 (Padrão 68: 1/27 vizinhos)**, atende 5 e 9.

## Resumo final V2/RAIO 15 ciclos

- 18 ADRs (0212-0230). 17 padrões (52-68; P57 retroativamente refutado).
- 1 SURVIVOR genuíno (S12 SOL — V1 inheritance).
- 5 GRAVEYARDs após pipeline (P52 + P50 cluster + EX001 + EX009 em S12 + ahora **S12+trail40 → QUARANTINED Padrão 68**).
- 1 SCOUTING+ validado (EX004 trail40 — confirmado direção positiva).
- 2 candidatos retirada urgente (S10/S11 paper-trade observation 14d).
- **0 strategies V2 fresh promovidas a manifest.**
- ~398 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~46min wall-clock total.
- 4 engines novos.
- AGENTS.md V2 guideline expandida (Padrões 53-68).

## Consequences

- **Positive:** pipeline V2 capturou último falso positivo aparente (S12+trail40). Padrão 68 é gate adicional valioso — single-point optima são endemic em V1 selection. Methodology guideline V2 mais robusta agora.
- **Negative:** após 15 ciclos rigorosos, zero strategies promovíveis. Indica que o universo (engines existentes V1 + datasets disponíveis) não contém edges robustos sob metodologia V2 estrita. Caminhos forward: (a) implementar engines novos (liquidity_trap, sizing_layer, regime_meta), (b) ingest novos dados (orderbook, funding, multi-asset signals), (c) ADR de gate-relax aceitando Padrão 60 reformulado.
- **Neutral:** stack V1 permanece operational sob protocolo paper-trade observation (ADR-0224). S12 SOL ainda gera trades real em paper-trade — observe-se até evidência operational decisiva.

## Próximas frentes (Cycle 16+ autopilot)

1. **2026-05-10**: ADR-0231 verdict S10/S11 paper-trade.
2. **Implementar liquidity_trap engine** (LQ001/LQ002 Top 18-19 V2). Pattern wrapper estabelecido. Custo ~3-5h. **Maior família V2 ainda intocada com mecanismo causal genuinamente novo (não param-sweep).**
3. **EX011 MAE-quantile exit** (4o wrapper, mesma pattern). Score ~7.0.
4. **ADR de gate-relax discussion**: aceitar Padrão 60 reformulado (Sh ≥ 1.0 + AND-criteria 1-9) como gate suficiente para promotion paper-trade observation extended. Pendente input user.

Recomendação Cycle 16: **opção 2 (liquidity_trap engine)**. Razão: 9 ciclos sucessivos refutando V1 inheritance; única forma de produzir candidate genuíno é mecanismo causal **fundamentalmente novo** (sweep/false breakout/exhaustion), não param tweaks de bollinger/rsi/etc.

## Não-alvo

- Não tentar mais Sensitivity em S12 — Padrão 68 é claro.
- Não retirar S12 do stack V1 — paper-trade ainda em curso (ADR-0224 cobre S10/S11; S12 fica até evidência operational decisiva).
- Não relax Padrão 68 (75% pass-rate) sem evidência empírica adicional.
- Não promover S12+trail40 sem ADR explícito gate-relax + paper-trade prolongado.

## Padrões totais: 68

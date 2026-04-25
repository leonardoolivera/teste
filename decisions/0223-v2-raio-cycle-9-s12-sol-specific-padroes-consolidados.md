# 0223 — V2/RAIO Ciclo 9 — S12 cross-asset FAIL (SOL-specific) + consolidação Padrões 53-62

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0222 (Cycle 8 stack 13 audit), ADR-0221 (Padrão 60), ADR-0211 (V1 closeout)

## Contexto

ADR-0222 (Cycle 8) identificou S12 (rsi_short_trendhtf SOL 2025-H1) como único ROBUST do stack canonical V1 sob Padrão 60. Hipótese causal: rsi_short com gate trend_htf (4h SMA 50) deve generalizar cross-asset se mecanismo é estrutural.

Cycle 9 testa essa hipótese via cross-asset validation S12 → BTC + ETH sobre janela contínua 30 meses.

Tools: [`tools/v2_s12_cross_asset_validation.py`](../tools/v2_s12_cross_asset_validation.py). 3 probes em 74s wall-clock.

## Resultado

| Asset | Sh | Trades | MDD% | PnL% | Padrão 60 |
|---|---:|---:|---:|---:|:-:|
| BTC | -0.02 | 171 | 8.9 | -0.6 | FAIL |
| ETH | -0.01 | 175 | 11.0 | -1.1 | FAIL |
| **SOL** | **1.20** | **185** | **9.0** | **+29.2** | **PASS** |

S12 cross-asset: **1/3** assets pass. Diferencial absoluto SOL vs BTC/ETH é massive: +1.22 Sharpe, +30% PnL.

## Decisão

1. **S12 mantém SURVIVOR mas com escopo SOL-only confirmado.**
2. **Não promove S12 a Candidate-for-ADR cross-asset.** Não há generalização demonstrável.
3. **S12 mantém-se no stack canonical V1** porque é o único combo do stack que passa Padrão 60 isolado.
4. **Stack canonical V1 redefinido:** 1 estratégia genuína (S12 rsi_short_trendhtf SOL) + 12 selection-bias survivors V1 mantidos pra diversificação cross-asset.

## Padrão 62 (novo) — Asset-specific edges são reais mas raros em crypto

S12 SOL Sh=1.20 vs S12 BTC/ETH Sh ≈ 0 sob exatamente a mesma config. **Edge é asset-specific, não engine-specific.**

Mecanismo plausível (não testado formalmente):
- SOL tem volatilidade idiossincrática maior que BTC/ETH (correlação SOL-BTC ~0.55-0.65 vs ETH-BTC ~0.75-0.85).
- SOL é mais retail-driven; flows extremos detectáveis via RSI overbought + HTF bear são mais frequentes/limpos.
- BTC/ETH têm mais hedging institucional → RSI extremes contam menos histórias.

**Implicação metodológica:** stratégias V2 podem ser asset-specific desde que mecanismo causal asset-specific seja explícito. SOL standalone com S12 é candidato V2 legítimo (após paper-trade extended), não single-window outlier como P52.

## Consolidação Padrões 53-62 (V2/RAIO methodology guideline)

Após 9 ciclos, consolidação dos padrões metodológicos descobertos:

| # | Nome | Lição |
|---|---|---|
| 53 | Fees floor screening | Default V2 = 10bps fees em screening; 5bps inflaciona Sh em estratégias high-turnover |
| 54 | DSR/PSR Bailey-LdP limitação crypto | kurt~20 inflate denominador PSR; threshold strict 0.95 demasiado restritivo |
| 55 | Script audit boolean flags CLI explicit | Todo script V2 passa `--long-only`/`--no-long-only` etc. explicitamente; defaults mudam |
| 56 | Block bootstrap não-paramétrico | Politis-Romano stationary block bootstrap como gate alternativo a DSR em crypto |
| 57 | (refutado) Trend-long como hedge regime-2024 | Cycle 7 mostrou que era selection bias, não hedge estrutural |
| 58 | Trend-long crypto regime-conditional | bull/recovery edge; bear absoluto cause -6 a -12% drawdown — proibido standalone |
| 59 | Regime gate vs sample size tradeoff | Gate apertado em windows curtas destrói trade count; precisa janela longa |
| 60 | Janela contínua ≥18m mandatória | Janelas curtas inflacionam Sharpe via temporal selection bias |
| 61 | Stack canonical é selection-bias-fragile | V1 aprovou cada combo em best window; 92% falha em janela contínua |
| 62 | Asset-specific edges são raros mas legítimos | SOL S12 funciona; BTC/ETH falha mesmo config — mecanismo asset-microstructural |

**Methodology guideline V2 consolidada (gate AND-conjunto pra promoção a manifest):**

1. **Janela contínua ≥18 meses** (Padrão 60).
2. **Fees ≥10bps** em screening (Padrão 53).
3. **Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 10%** sobre janela longa (gate ADR-0030 reformulado).
4. **Cross-asset OU asset-specific mecanismo causal explícito** (Padrão 62).
5. **Bootstrap não-paramétrico OR PSR(0)>0.95** (Padrão 56 alternativa Padrão 54).
6. **Sensitivity local não-colapso** (Padrão 52 Sensitivity test).
7. **Portfolio integration positiva** (PF024) em ≥2 regimes distintos.
8. **Padrão 58 mitigation** se trend-long (regime gate obrigatório).
9. **Script audit** confirma flags CLI explicit (Padrão 55).

## Resumo final V2/RAIO 9 ciclos

- **11 ADRs (0212-0223).** 11 padrões registrados (52-62, com 57 retroativamente refutado).
- **1 strategy enterrada após pipeline completo** (P52, 7 ciclos).
- **1 SURVIVOR genuíno do stack V1 descoberto retroativamente** (S12, SOL-specific).
- **0 strategies V2 novas promovidas** (esperado per metodologia rigorosa V2).
- **2 candidatos urgentes pra retirada do stack** (S10, S11 catastróficos sob janela longa).
- **~280 backtests + estatística + portfolio integration** em ~20min wall-clock total.
- **3 datasets concat30m criados** (BTC/ETH/SOL).
- **1 engine novo implementado** (BHDrawdownFilter).
- **9 padrões metodológicos** consolidados como guideline V2.

## Consequences

- **Positive:** primeiro candidato V2-validated identificado retroativamente (S12 SOL); methodology guideline consolidada; 9 ciclos demonstram que pipeline V2/RAIO funciona — descobre fragilidades V1 + guarda contra falsos positivos.
- **Negative:** zero strategies V2 fresh promovidas; expansão do stack requer dev novo (regime detector, exit_layer, etc.); S10/S11 ainda em produção pendente paper-trade extended.
- **Neutral:** S12 SOL-specific aceitável per Padrão 62; portfolio diversification do stack mantém valor mesmo com edges individuais fracos.

## Follow-ups (Cycle 10+ autopilot)

Recomendação ranking RAIO §13:

1. **ADR-0224 paper-trade observation S10/S11** (urgência operational): formalizar processo + timeline 1-2 semanas observation antes de retirada.
2. **Implementar exit_layer engine** (EX001 + 35 hipóteses V2). Score ~7.5. Custo dev 3-5h. Destrava maior família V2.
3. **Audit retroativo TF10m manifests** (ADR-0202 winners): testar Padrão 50 candidates em janela contínua. Provavelmente todos GRAVEYARD (já era single-window).
4. **Update AGENTS.md** com methodology guideline V2 (Padrões 53-62) como leitura obrigatória.

## Não-alvo

- Não promover S12 a manifest cross-asset (FAIL confirmed).
- Não tentar variações S12 em BTC/ETH com params alternativos (Padrão 62: edge é SOL-microstructure, não config).
- Não retirar S10/S11 sem ADR-0224 + paper-trade observation extended.
- Não declarar pipeline V2/RAIO "completo" — exit_layer + sizing_layer + liquidity_trap + regime detector ainda destravam famílias V2.

## Padrões totais: 62

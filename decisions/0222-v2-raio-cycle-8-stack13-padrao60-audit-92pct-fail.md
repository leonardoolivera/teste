# 0222 — V2/RAIO Ciclo 8 — Stack 13 audit retroativo: 12/13 falham Padrão 60 + Padrão 61

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0221 (Padrão 60 + P52 GRAVEYARD), ADR-0216 (errata stack 13 fee stress), ADR-0030 (export gates)

## Contexto

Cycle 7 (ADR-0221) estabeleceu **Padrão 60**: janela contínua ≥18 meses é mandatória para promoção V2; janelas curtas (≤6 meses) inflacionam Sharpe via temporal selection bias. P52 morto após audit em 30m window.

Cycle 8 aplica retroativamente Padrão 60 ao **stack canonical V1** (13 manifests aprovados, base de produção e handoffs BotBinance). Hipótese: alguns combos podem ser P52-like, edges intra-window que evaporam em janela longa.

Tools: [`tools/v2_stack13_padrao60_audit.py`](../tools/v2_stack13_padrao60_audit.py). 13 probes × janela contínua 30m × fees 10bps = ~90s wall-clock.

## Resultado

| ID | Manifest | Sym | Sh | Tr | MDD% | PnL% | Verdict |
|---|---|---|---:|---:|---:|---:|:-:|
| S01 | bollinger_width_regime_v2 | ETH | 0.89 | 189 | 5.5 | +12.5 | MARGINAL |
| S02 | bollinger_width_regime_v2 | ETH | 0.89 | 189 | 5.5 | +12.5 | MARGINAL |
| S03 | bollinger_width_regime_v2 | BTC | 0.62 | 109 | 4.0 | +5.5 | MARGINAL |
| S04 | bollinger_width_regime_v2 | SOL | 0.25 | 239 | 10.4 | +4.0 | FAIL |
| S05 | bollinger_short_width | SOL | 0.46 | 523 | **14.5** | +12.6 | FAIL |
| S06 | bollinger_short_width | BTC | 0.11 | 244 | 7.2 | +1.0 | FAIL |
| S07 | bollinger_short_width | ETH | 0.55 | 389 | **15.0** | +10.4 | FAIL |
| S08 | bollinger_short_width | SOL | 0.46 | 523 | **14.5** | +12.6 | FAIL |
| S09 | rsi_long_width_eth_2024h2 | ETH | **-0.09** | 183 | 7.4 | **-1.5** | FAIL |
| S10 | rsi_short_pure_2025h2 | BTC | **-0.58** | 424 | **22.0** | **-11.7** | FAIL |
| S11 | rsi_short_pure_2025h2 | SOL | **-0.38** | 392 | **35.9** | **-16.8** | FAIL |
| **S12** | **rsi_short_trendhtf_sol_2025h1** | **SOL** | **1.20** | **185** | **9.0** | **+29.2** | **ROBUST** |
| S13 | rsi_short_width_2025h1 | BTC | 0.42 | 234 | 9.7 | +4.8 | FAIL |

**Counts:**
- **1/13 ROBUST (8%)** — apenas S12 (rsi_short_trendhtf SOL 2025-H1).
- **3/13 MARGINAL (23%)** — S01, S02, S03 (bollinger_width_regime_v2 long-only ETH/BTC).
- **9/13 FAIL (69%)** — incluindo 3 com PnL negativo (S09, S10, S11).

**S10 + S11 (rsi_short_pure_2025h2 BTC + SOL) particularmente alarmantes:**
- BTC: Sh=-0.58, MDD=22%, PnL=-11.7% sobre 30 meses.
- SOL: Sh=-0.38, **MDD=36%**, PnL=-16.8%.
- Esses dois manifests aprovados V1 são **catastróficos** sob janela contínua. Discovery em 2025-H2 isolada (Sh=1.64) era selection bias temporal puro.

## Decisão

1. **Padrão 60 confirmado retroativamente sobre 12/13 do stack** (92% do stack canonical V1 sofre do mesmo selection bias que P52 GRAVEYARD).
2. **S12 (rsi_short_trendhtf SOL 2025-H1) é único survivor genuíno do stack V1 sob critério V2.**
3. **S10 e S11 são candidatos urgentes para retirada do stack:**
   - PnL negativo + drawdowns 22-36% sobre janela contínua.
   - Risco material em produção paper-trading se sequência adversa do tipo 2023-H2 ressurgir.
   - Recomendação: **flag pra remoção em próxima atualização do stack canonical**. Paralelamente, **paper-trade prolongado** desses dois para confirmar a degradação observada não é artefato de re-execução.
4. **S04-S08, S13 (stack MR core)**: manter mas reconhecer fragilidade structural — Sharpe individual 0.11-0.55 em janela longa = baixíssimo edge isolado. Sobreviver no stack depende exclusivamente de **diversificação cross-asset** (correlações negativas reduzem MDD conjunto).
5. **S01-S03 (bollinger_width_regime_v2 long-only)** são os 3 melhores não-robust — Sh ~0.62-0.89, mais perto de gate Padrão 60.
6. **NÃO export novos combos** baseados em metodologia V1 (single window) sem re-validação Padrão 60.

## Padrão 61 (novo) — Stack canonical é selection-bias-fragile

V1 aprovava combos individuais cada em 1 window favorável (cada source_run_id é uma window de 6 meses). Stack 13 = união de 13 selections locais. Em janela contínua 30m unificada, 12/13 perdem edge.

**Mecanismo causal:** cada manifest V1 era a "best window" para aquela combo (asset, engine, params). Selection sobre 7+ semestres × 3+ assets × 5+ engines × N params = espaço enorme; 13 vencedores são tail dessa distribuição. Aplicar a mesma combo em window não-discovery é regression-to-mean estatística.

**Implicação operational:**
- Stack 13 funciona em paper-trade hoje porque diversificação cross-asset + correlações negativas amortecem perdas individuais.
- Se mercado entra em regime extremo de correlation surge (e.g. risk-off coordenado), perdas individuais somam — stack quebra.
- Padrão 61 ⊥ Padrão 60: ambos sinalizam que metodologia V1 (single-window approval) é frágil; metodologia V2 (janela contínua + cross-era + bootstrap + portfolio integration + Padrão 60) é o que entrega manifests robustos.

## Consequences

- **Positive:** auditoria Padrão 60 sobre stack canonical revelou fragilidade estrutural. V1 stack está em produção mas não passaria gate V2. Pipeline V2 captou isso ANTES de qualquer ampliação ou re-export.
- **Negative:** stack canonical em produção tem 9/13 combos abaixo de Padrão 60. Recomendação de retirada de 2 (S10, S11) requer ADR de paper-trade observation extended. Pode reduzir stack V1 efetivo de 13 para 11 combos.
- **Neutral:** S12 é único candidate validado V2. Padrão 60 + Padrão 61 viram doctrine permanente para próximas séries de pesquisa.

## Follow-ups (Cycle 9+ autopilot)

- **ADR de remoção S10+S11 do stack canonical** — requer paper-trade observation extended (1-2 semanas) ANTES de retirada definitiva.
- **Re-validação S12 sob Padrão 60 cross-asset:** S12 é SOL specific; testar `rsi_short_trendhtf` em ETH e BTC sobre 30m window. Se passar, S12 vira primeiro genuíno V2-validated combo.
- **Próxima frente RAIO grande:** implementar exit_layer engine (EX001-036, ~36 hipóteses V2 destravadas). Score ~7.5. Custo dev 3-5h.
- **ADR-0223 (futuro):** consolidar Padrões 53-61 como methodology guideline V2 permanente. Update AGENTS.md/STATE.md leitura obrigatória para próximas sessões.

## Não-alvo

- Não retirar S10/S11 do stack hoje sem paper-trade observation extended (risco de remoção precipitada).
- Não promover S12 sem cross-asset validation (regime-specific risk).
- Não ampliar stack 13 com novos combos V1-style sem Padrão 60 obrigatório.
- Não export S01-S03 marginais — Sh < 1.0 não atinge gate.

## Padrões totais: 61

# 0221 — V2/RAIO Ciclo 7 — P52 GRAVEYARD após janela contínua 30 meses + Padrão 60

**Status:** Accepted (verdict final P52)
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0220 (BHDrawdownFilter Cycle 6 + Padrão 59), ADR-0219 (cross-era FAIL), ADR-0218 (PF024 PASS), ADR-0217 (P52 SURVIVOR), ADR-0214 (P52 PROMISING)

## Contexto

ADR-0220 introduziu BHDrawdownFilter (Padrão 58 mitigation) e identificou Padrão 59 (regime gate vs sample size tradeoff): em windows de 6 meses, gate apertado destrói trade count. Cycle 7 implementou solução: testar P52 + bh_drawdown sobre **janela contínua 30 meses** (2023-H2 a 2025-H2).

Tools criados:
- [`tools/v2_concat_extended_datasets.py`](../tools/v2_concat_extended_datasets.py): merge BTC/ETH/SOL 1h em datasets concat30m (21,672 bars). Declared gaps em 2024-01-01..04 e 2025-01-01..04 (boundary entre semestres).
- [`tools/v2_p52_gate_extended_window.py`](../tools/v2_p52_gate_extended_window.py): P52 18/60 raw + 3 thresholds bh_drawdown sobre 30m window.

12 probes (3 assets × 4 variants) em 17s wall-clock.

## Resultado

| Asset | Variant | Sharpe | Trades | MDD% | PnL% | Pass gate |
|---|---|---:|---:|---:|---:|:-:|
| BTC | raw | -0.08 | 171 | 13.0 | -1.5 | ❌ |
| BTC | dd15 | 0.08 | 124 | 9.7 | 0.6 | ❌ |
| BTC | dd25 | 0.03 | 142 | 11.4 | 0.1 | ❌ |
| BTC | dd35 | 0.05 | 143 | 11.2 | 0.3 | ❌ |
| ETH | raw | 0.67 | 162 | 14.2 | +11.9 | ❌ |
| **ETH** | **dd15** | **0.83** | 81 | **6.0** | 10.8 | ❌ (Sh<1.0) |
| ETH | dd25 | 0.54 | 122 | 11.5 | 8.0 | ❌ |
| ETH | dd35 | 0.38 | 137 | 12.1 | 5.7 | ❌ |
| SOL | raw | 0.29 | 163 | 17.6 | 5.8 | ❌ |
| **SOL** | **dd15** | **0.87** | 74 | **6.6** | **+14.0** | ❌ (Sh<1.0) |
| SOL | dd25 | 0.06 | 112 | 13.4 | 0.2 | ❌ |
| SOL | dd35 | 0.05 | 133 | 16.9 | -0.1 | ❌ |

Gate ADR-0030 reformulado (Sh ≥ 1.0 ∧ trades ≥ 30 ∧ MDD ≤ 5%): **0/12 PASS.**

### Padrão 58 mitigation — VALIDADA quantitativamente

bh_drawdown(15%) cumpre seu objetivo:
- ETH: MDD 14.2 → 6.0 (-58%), Sh 0.67 → 0.83 (preservado/melhorado)
- SOL: MDD 17.6 → 6.6 (-62%), Sh 0.29 → 0.87 (boost massivo)
- BTC: improvement marginal (P52 não funciona em BTC além de 2024-H2)

bh_drawdown(15%) é **the tightest threshold tested** e dominante; bh_drawdown(25%/35%) diluem o sinal.

### MAS — P52 não vence o gate

Mesmo com gate ótimo (dd15) em ETH/SOL: Sh atinge 0.83-0.87, abaixo do gate Sh ≥ 1.0. **Edge real do P52 é insuficiente para promoção** sob critério V2.

## Padrão 60 (novo) — Janela longa contínua é gold standard

Cycle 1-3 declararam P52 SURVIVOR + Candidate-for-ADR baseado em window 2024-H2 (6 meses). Cycle 4 PF024 PASS Sh=3.02 também era 2024-H2. Cycle 7 sobre 30 meses contínuos: Sh=-0.08 a 0.87 (todos abaixo de 1.0).

**Lição:** janelas curtas (≤ 6 meses) inflacionam Sharpe via selection bias temporal. Para promoção V2:
- **Mandatório:** validação em janela contínua ≥ 18 meses (cobre múltiplos regimes intra-cycle).
- **Sufficient:** Sh ≥ 1.0 com trade count ≥ 30 + MDD ≤ 5% em ≥ 2 assets.
- **Tradeoff aceito:** baixa taxa de promoção (Sh > 1.0 sustained 18+ meses crypto é raro).

## Decisão final P52

**P52 → GRAVEYARD.** Trajetória completa (7 ciclos):

| Ciclo | Verdict |
|---|---|
| 1 (RB004 cross-era 6m) | PROMISING (2/6 BTC+SOL 2024-H2 pass) |
| 2 (Sensitivity 48 vizinhos) | 100% Sh ≥ 0.94 — Vizinhança positiva |
| 3 (Bootstrap 1000 reps) | 8/48 STRONG; BTC 18/60 CI95=[0.04, 5.94] → SURVIVOR |
| 4 (PF024 add-one stack 13) | PF024 PASS Sh +60%, MDD -20% → Candidate for ADR |
| 5 (Cross-era windows 6m) | FAIL bear 2022 (Sh -2.85), FAIL 2024-H1, marginal 2023-H2 SOL |
| 6 (BHDrawdownFilter intro) | Gate funciona (-90% MDD bear) mas tr<30 em windows 6m |
| **7 (janela contínua 30m)** | **Sh ≤ 0.87 todas configs — FAIL gate** |

**Causa de morte:** edge intra-2024-H2 (Sh 3.02) era artefato de selection bias temporal. Em janela contínua 30 meses cobrindo bull/recovery/bear: Sh vai a zero. Padrão 58 mitigation reduz MDD efetivamente, mas P52 não tem signal robusto longo prazo.

**Não-reabrir** P52 sem:
- Mecanismo causal específico para regime detectável que sobreviva 18+ meses contínuos.
- Backtest em data nova (não disponível em datasets atuais).

## Patterns updated

- **Padrão 52** (ma_crossover 18/60): GRAVEYARD após 7 ciclos. Edge regime-2024-H2 specific, não generaliza temporalmente.
- **Padrão 53** (fees floor): mantido.
- **Padrão 54** (DSR/PSR Bailey-LdP limitação): mantido.
- **Padrão 55** (script audit boolean flags): mantido.
- **Padrão 56** (block bootstrap não-paramétrico): mantido como gate alternativo.
- **Padrão 57** (trend-long como hedge regime-2024): retroativamente refutado em janela longa.
- **Padrão 58** (regime-conditional trend-long crypto): mantido + **mitigação validada** (bh_drawdown 15% reduz MDD ~60%, mas Sh insuficiente).
- **Padrão 59** (gate vs sample size tradeoff): mantido.
- **Padrão 60 (novo):** Janela contínua ≥ 18 meses obrigatória para promoção V2. Janelas curtas inflacionam Sharpe via selection bias temporal.

## Consequences

- **Positive:** primeiro CUT formal de strategy V2/RAIO. Pipeline rigoroso entregou: 7 ciclos, 8 ADRs, 9 patterns. Demonstrou que stack canonical V1 (ADR-0216 fix) é mais robusto que candidates V2 testados — bom signal sobre maturidade do stack canonical.
- **Negative:** zero strategies V2/RAIO promovidas a manifest após 7 ciclos. P52 era único candidato real; resto da árvore é backlog (regime detectors, exit_layer, sizing_layer, liquidity_trap). Custo dev pra atacar próximas raízes é maior.
- **Neutral:** Padrão 60 (janela contínua) reformula gate V2 — todos próximos candidates devem ser testados em 30m windows desde início. Cycles 1-3 metodologia (window 6m) é insuficiente por si só.

## Próximas frentes (Cycle 8+ autopilot)

Per RAIO §13 anti-pergunta + score:

1. **Implementar exit_layer engine** (atende EX001 time stop curto + 35 outras EX hipóteses do V2). Score ~7.5. Custo dev: ~3-5h. Destrava maior família V2.
2. **Implementar sizing_layer engine** (PS001-027 hipóteses). Score ~6.5. ADR-0030 invariantes proíbem sizing dinâmico em produção; pesquisa ok.
3. **Implementar liquidity_trap engine** (LQ001-027). Score ~7.0. Top 18-19 V2 (LQ001/LQ002 falso rompimento).
4. **Re-rodar todos os 13 manifests aprovados sobre janela contínua 30 meses** (Padrão 60 application). Audit retroativo do stack canonical sob critério V2 corrigido. Score ~7.0. Custo: ~5min wall-clock (mesmo workflow PF024).

Recomendação Cycle 8: **opção 4 (audit retroativo stack 13 sob janela 30m)**. Razão:
- Custo zero código (reusa scripts existentes + concat datasets já criados).
- Resultado de alto valor: descobre se stack 13 atual é robusto pelo critério V2 ou se foi aprovado em janela curta análoga ao P52.
- Decisão downstream: se stack 13 falha gate V2 em janela longa, retira manifests problemáticos antes de export futuro.

## Não-alvo

- Não export P52 em qualquer forma (gate ADR-0030 confirmed FAIL, agora no Padrão 60 também).
- Não tentar P52 + outros gates (e.g. trend_htf, atr_regime) — Padrão 60 já mostra que edge não existe em janela longa.
- Não relaxar Padrão 60 para "salvar" P52 — disciplina V2 mantida.
- Não considerar P52 reabrir até dados pós-2025-H2 (futuro) com mecanismo causal pré-declarado.

## Padrões totais: 60

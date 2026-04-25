# 0035 — Sensibilidade do `min_width_bps` regime gate: resultados da Série BO e Pareto 3D

**Status:** Superseded — resultados invalidados por ADR-0037, re-derivados em ADR-0038
**Date:** 2026-04-19
**Deciders:** Usuário (owner do projeto) + agente.

> **ERRATA (2026-04-19):** Série BO original rodou regime filter com (window=20, num_std=2) em vez de (30, 1.5) do manifest. ADR-0037 documenta; ADR-0038 re-deriva Pareto 3D. Texto original preservado para auditoria — **não usar para decisões**. Notas críticas pós-correção: SOL 2024-H2 melhorou para `semi_robust_2d` (num_std + window); ETHUSDT weakest_wins agora = `fragile_3d`.

## Context

Séries BK (ADR-0032, num_std) e BN (ADR-0033, window) mapearam 2 eixos do Pareto dos 4 combos do manifest v2. A Série BO testa o 3º eixo: `min_width_bps` do regime filter `bollinger_width` (threshold que define se o regime está "contraído" o suficiente pra permitir sinais mean-reversion).

Matriz: `min_width_bps ∈ {200, 300}` × 4 combos × `window=30, num_std=1.5` fixos × regime filter internals (w=20, ns=2) fixos = 8 pilotos (BO.1–BO.8).

Perturbação ±20% do baseline `min_width_bps=250` escolhido em ADR-0028.

Gates strict idênticos às Séries BK/BN: `trades ≥ 30`, `Sharpe ≥ 1.0`, `MDD ≤ 20%`, `PnL > 0`, `cost_stress_ratio_min ≥ 0.95`, `MC p5 final_equity > 10000`, `MC MDD p95 ≤ 10%`.

## Resultados (resumo em `exports/diag/bo_sweep_summary.json`)

| Tag | Combo | bw | trades | Sharpe | MDD% | PnL% | cost_r | MC p5 eq | MC MDD p95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BO.1 | ETH 2024-H1 | 200 | 47 | 0.742 | 3.63 | +2.08 | 0.9762 |  9632 | 6.15 | FAIL (Sharpe, MC p5) |
| BO.2 | ETH 2025-H1 | 200 | 51 | 1.139 | 4.52 | +3.91 | 0.9724 |  9586 | 7.64 | FAIL (MC p5) |
| BO.3 | BTC 2024-H2 | 200 | 40 | 0.861 | 2.66 | +1.43 | 0.9782 |  9831 | 3.76 | FAIL (Sharpe, MC p5) |
| BO.4 | SOL 2024-H2 | 200 | 68 | 2.048 | 3.51 | +7.31 | 0.9697 | 10152 | 4.66 | **PASS** |
| BO.5 | ETH 2024-H1 | 300 | 37 | 1.683 | 1.97 | +4.10 | 0.9831 |  9950 | 3.40 | FAIL (MC p5) |
| BO.6 | ETH 2025-H1 | 300 | 40 | 2.073 | 3.79 | +6.08 | 0.9783 | 10075 | 3.39 | **PASS** |
| BO.7 | BTC 2024-H2 | 300 | 21 | 0.445 | 1.25 | +0.54 | 0.9856 |  9924 | 1.58 | FAIL (trades<30, Sharpe, MC p5) |
| BO.8 | SOL 2024-H2 | 300 | 54 | 1.525 | 3.64 | +4.63 | 0.9738 |  9915 | 5.29 | FAIL (MC p5) |

**Placar: 2/8 PASS → Pareto estreito.**

Por combo (2 perturbações cada):

| Combo | PASS bw=200 | PASS bw=300 | Classe min_width_bps |
|---|---|---|---|
| ETH 2024-H1 | ❌ | ❌ | **fragile_both** |
| ETH 2025-H1 | ❌ (BO.2 MC p5) | ✅ (BO.6 Sharpe 2.07) | fragile_low |
| BTC 2024-H2 | ❌ | ❌ (BO.7 trades=21) | **fragile_both** |
| SOL 2024-H2 | ✅ (BO.4 Sharpe 2.05) | ❌ (BO.8 MC p5) | fragile_high |

## Análise — Pareto 3D consolidado

Combinando ADR-0032 (num_std) + ADR-0033 (window) + este ADR (min_width_bps):

| Combo | num_std | window | min_width_bps | Classe 3D |
|---|---|---|---|---|
| ETH 2024-H1 | fragile_high | fragile_both | fragile_both | **fragile_3d_totalmente_frágil** |
| ETH 2025-H1 | **robust** | fragile_low | fragile_low | semi_robust_num_std |
| BTC 2024-H2 | fragile_both | fragile_low | fragile_both | fragile_3d |
| SOL 2024-H2 | fragile_low | **robust** | fragile_high | semi_robust_window |

**Achado crítico: o eixo `min_width_bps` é o mais estreito dos 3.** Apenas 2/8 pilotos passam — vs 4/8 em BK e BN. Isso sugere que `min_width_bps=250` não foi escolhido cegamente no ADR-0028: é genuinamente próximo de um ponto ótimo do gate. Mas também significa que:

1. **O regime gate está no limiar de toda a performance.** Deslocar ±20% quebra 75% dos combos. Alta alavancagem do parâmetro.
2. **A assimetria observada em BK e BN se mantém em BO:** ETH 2025-H1 prefere gate mais restritivo (bw=300), SOL 2024-H2 prefere mais permissivo (bw=200). Eles se comportam de forma espelhada em múltiplos eixos.
3. **BTC é consistentemente frágil nos 3 eixos.** Em bw=300, BTC só gera 21 trades < 30 — perde até o gate de volume. Confirma pela 3ª vez (ADR-0029, 0032, 0033) que BTC 2024-H2 é ativo estruturalmente marginal para esta estratégia.

## Classificação 3D final por combo

- **ETH 2024-H1:** `fragile_3d_totalmente_frágil` — frágil em todos os 3 eixos. Candidato #1 para suspensão se paper mostrar qualquer sinal ruim.
- **ETH 2025-H1:** `semi_robust_num_std` — robust em 1 eixo (num_std), frágil nos outros 2. Não é robust 2D como o ADR-0033 sugeriu.
- **BTC 2024-H2:** `fragile_3d` — frágil nos 3, mas com padrão BTC estrutural (trades<30 recorrente). Candidato #1 para suspensão em live antes de ETH 2024-H1.
- **SOL 2024-H2:** `semi_robust_window` — robust em 1 eixo (window), frágil nos outros 2.

## Decision

1. **Manter manifest v2 intacto em `approved_combos` e `engine.params.regime_filter`.** `min_width_bps=250` é um ponto estreito do Pareto, mas mover agora seria otimização retroativa. Observação empírica não justifica re-aprovação.

2. **Adicionar campo `robustness.min_width_bps_sensitivity`** em cada combo do manifest v2:
   - ETH 2024-H1 → `fragile_both`
   - ETH 2025-H1 → `fragile_low`
   - BTC 2024-H2 → `fragile_both`
   - SOL 2024-H2 → `fragile_high`

3. **Atualizar `robustness.cross_axis_2d` → `cross_axis_3d`**:
   - ETH 2024-H1 → `fragile_3d_totalmente_frágil`
   - ETH 2025-H1 → `semi_robust_num_std` (mantém)
   - BTC 2024-H2 → `fragile_3d`
   - SOL 2024-H2 → `semi_robust_window` (mantém)

4. **O critério weakest-wins do ADR-0034 continua válido.** `rollout_priority_live` não muda — ETHUSDT e BTCUSDT continuam `fragile_2d`/`fragile_3d` em live, SOL continua `semi_robust_window`. A diferença é só a qualidade da informação offline agora.

5. **Revisão do critério da 2ª onda (BTC):** Como BTC falha em 3/3 eixos, considerar elevar o critério da 2ª onda de `14 dias` para `21 dias` de paper limpo antes de adicionar BTC. Sugestão para o @botbinance — não decidido unilateralmente.

6. **Hipóteses colaterais acumuladas para Série BP (se conduzida):**
   - ETH 2025-H1 com `(window=35, num_std=1.5, bw=300)` poderia dar Sharpe > 3 baseado em 3 sinais convergentes (BK.6, BN.6, BO.6).
   - ETH 2024-H1 com `(window=30, num_std=1.25, bw=?)` baseado em BK.1.
   - SOL 2024-H2 com `(window=?, num_std=1.75, bw=200)` baseado em BK.8 + BO.4.
   - **Não acionar.** Série BP precisaria de train/val/test isolado (novo semestre hold-out) pra não ser data snooping sobre o que já foi visto.

## Consequences

**Prós:**
- Pareto 3D mapeado empiricamente. Risco de overfitting do ADR-0028 agora é mensurável e documentado.
- Confirma padrão BTC "ativo estruturalmente marginal" em 3 eixos independentes. Forte base empírica pra elevar critério da 2ª onda.
- SOL e ETH 2025-H1 mostram assimetria espelhada consistente em 3 eixos — sinal de que têm modos de falha diferentes. Continua sendo boa diversificação em live.

**Contras:**
- A conclusão pratica é que o config aprovado v2 é **próximo de um ótimo local em todos 3 eixos**, o que aumenta o risco de quebra se o regime de mercado mudar mesmo levemente. Não temos folga paramétrica — o config é fino.
- 3 eixos testados e nenhum combo `robust` em todos. A noção de "carro-chefe robusto" está oficialmente morta.

**Riscos residuais:**
- Efeitos de interação entre eixos não testados (BP). Perturbação 2-axis pode dar resultado diferente de soma de perturbações 1-axis.
- `trades` como gate duro expõe BTC em múltiplos eixos (BN.3=29, BO.7=21, BK.7=31). Sugere que o critério de volume deveria ser re-pensado para BTC especificamente, ou BTC deveria sair do manifest de deploy mean-reversion por completo.

## Follow-ups

- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json` com `robustness.min_width_bps_sensitivity` + `robustness.cross_axis_3d` por combo.
- [ ] Notificar @botbinance no bridge com resultado + sugestão de elevar critério 2ª onda de 14d → 21d.
- [ ] Fechar Série BO (`agentic/active/SERIES_BO.md`).
- [ ] **Pausar sweeps.** 3 eixos 1D × 8 pilotos cada = 24 pilotos mapeados. Próximo experimento útil só depois de:
  - (a) 5+ trades live em paper pra comparação runtime vs AF canonical, OU
  - (b) import dos datasets ARB/UNI/LINK/POL para atacar Cat B, OU
  - (c) port das estratégias `volume_breakout` e `stoch_rsi_cross` para o AF.
  Séries BP (interação 2-axis) e BL (cross-timeframe 4h) ficam de lado até (a/b/c) acontecer.

## Artefatos

- Sweep raw: `results/validation/bo-dryrun-w30-ns150-bw{200,300}-*` (8 dirs).
- Sweep summary: `exports/diag/bo_sweep_summary.json`.
- Script: `tools/run_bo_sweep.py`.
- Série brief: `agentic/active/SERIES_BO.md`.

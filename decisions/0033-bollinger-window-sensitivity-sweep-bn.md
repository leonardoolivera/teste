# 0033 — Sensibilidade do `window` Bollinger: resultados da Série BN e Pareto 2D cross-axis

**Status:** Superseded — resultados invalidados por ADR-0037, re-derivados em ADR-0038
**Date:** 2026-04-19
**Deciders:** Usuário (owner do projeto) + agente.

> **ERRATA (2026-04-19):** Mesma causa raiz da Série BK (ver ADR-0032 errata): regime_filter rodou com defaults (20/2) em vez do manifest (30/1.5). ADR-0037 documenta o bug, ADR-0038 traz nova Pareto 2D corrigida. Texto original preservado para auditoria — **não usar para decisões**. Nota crítica: ETH 2025-H1 perdeu classificação `semi_robust_num_std` (era artefato); nova classe = `fragile_3d_totalmente_fragil`.

## Context

Após a Série BK (ADR-0032) mapear o eixo `num_std` dos 4 combos aprovados no manifest v2, abriu-se a Série BN para o eixo `window`. Matriz: `window ∈ {25, 35}` × 4 combos × `num_std=1.5` fixo × regime gate bw_250 inalterado = 8 pilotos (BN.1–BN.8).

Objetivo: fechar o Pareto 2D (`window × num_std`) antes de qualquer rollout paper.

Gates strict idênticos à Série BK: `trades ≥ 30`, `Sharpe ≥ 1.0`, `MDD ≤ 20%`, `PnL > 0`, `cost_stress_ratio_min ≥ 0.95`, `MC p5 final_equity > 10000`, `MC MDD p95 ≤ 10%`.

Critério decisório pré-estabelecido:
- ≥ 6/8 PASS → Pareto robusto no `window`; nota informativa no ADR-0032.
- 3–5/8 PASS → Pareto médio; **este ADR** marca fragilidade 2D.
- ≤ 2/8 PASS → Pareto estreito; ADR depreca combos frágeis.

## Resultados (resumo em `exports/diag/bn_sweep_summary.json`)

| Tag | Combo | w | trades | Sharpe | MDD% | PnL% | cost_r | MC p5 eq | MC MDD p95% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| BN.1 | ETH 2024-H1 | 25 | 45 | 0.868 | 3.85 | +2.38 | 0.9793 |  9752 | 5.17 | FAIL (Sharpe, MC p5) |
| BN.2 | ETH 2025-H1 | 25 | 55 | 1.676 | 4.26 | +5.46 | 0.9729 |  9945 | 4.85 | FAIL (MC p5) |
| BN.3 | BTC 2024-H2 | 25 | 29 | 2.376 | 1.26 | +3.40 | 0.9828 | 10211 | 0.86 | FAIL (trades<30) |
| BN.4 | SOL 2024-H2 | 25 | 72 | 1.859 | 3.54 | +6.20 | 0.9677 | 10167 | 4.18 | **PASS** |
| BN.5 | ETH 2024-H1 | 35 | 33 | 1.343 | 2.35 | +3.37 | 0.9854 |  9927 | 3.94 | FAIL (MC p5) |
| BN.6 | ETH 2025-H1 | 35 | 46 | 2.820 | 3.40 | +8.85 | 0.9781 | 10261 | 3.42 | **PASS** |
| BN.7 | BTC 2024-H2 | 35 | 30 | 2.244 | 1.94 | +3.26 | 0.9830 | 10152 | 1.24 | **PASS** |
| BN.8 | SOL 2024-H2 | 35 | 58 | 1.726 | 3.38 | +5.69 | 0.9733 | 10120 | 4.02 | **PASS** |

**Placar: 4/8 PASS** → Pareto médio (mesma classe de BK).

Por combo (2 perturbações cada):

| Combo | PASS w=25 | PASS w=35 | Classe window |
|---|---|---|---|
| ETH 2024-H1 | ❌ (BN.1) | ❌ (BN.5) | **fragile_both** |
| ETH 2025-H1 | ❌ (BN.2) | ✅ (BN.6) | fragile_low |
| BTC 2024-H2 | ❌ (BN.3 trades=29) | ✅ (BN.7) | fragile_low |
| SOL 2024-H2 | ✅ (BN.4) | ✅ (BN.8) | **robust** |

## Cross-axis (BK × BN) — Pareto 2D

Combinando ADR-0032 (num_std) + este ADR (window):

| Combo | num_std | window | Cross-axis |
|---|---|---|---|
| ETH 2024-H1 | fragile_high | fragile_both | **fragile_2d** |
| ETH 2025-H1 | **robust** | fragile_low | semi_robust |
| BTC 2024-H2 | fragile_both | fragile_low | **fragile_2d** |
| SOL 2024-H2 | fragile_low | **robust** | semi_robust |

**Achado crítico: nenhum combo é `robust` nos dois eixos.** Os dois combos "melhores"
do manifest v2 são semi-robustos em um único eixo cada:

- **ETH 2025-H1** é robusto em `num_std` (BK.2/BK.6 ambos PASS com folga: Sharpe 2.10/1.96) mas frágil no lado baixo de `window` (BN.2 falha MC p5 em w=25, porém passa cleanly em w=35 com Sharpe 2.82).
- **SOL 2024-H2** é robusto em `window` (BN.4/BN.8 ambos PASS) mas frágil no lado baixo de `num_std` (BK.4 falha MC p5 em ns=1.25, porém passa em ns=1.75 com Sharpe 2.23).

ETH 2024-H1 e BTC 2024-H2 são frágeis em ambos eixos — candidatos mais arriscados para paper.

## Análise

1. **BN.3 falha por `trades<30` (29 trades)**, não por edge. Sharpe 2.38 e MC p5 10211 são excelentes, mas o gate de volume exclui. Consistente com o padrão BTC "ativo lento" já observado em ADR-0029 (BTC 2025-H1) e ADR-0032 (BK.3/BK.7). Reduzir window piora o volume em BTC nesse regime.

2. **BN.7 passa com folga (Sharpe 2.24, 30 trades exatamente).** BTC em w=35 no limiar do gate — se alguma fold der −1 trade, o combo quebra. Sinal de robustez marginal, não real.

3. **SOL 2024-H2 é o único combo robusto ao eixo window em ambos lados** — passa tanto w=25 (Sharpe 1.86) quanto w=35 (Sharpe 1.73). Sugere que a mean-reversion SOL é insensível a suavização da janela no regime 2024-H2.

4. **ETH 2024-H1 falha simetricamente em ambos lados de `window`** (BN.1 Sharpe 0.87 + MC p5; BN.5 MC p5). Combinado com BK.5 (falha em ns=1.75), este combo mostra 3/4 falhas em perturbações de 1 eixo. É o combo mais marginal do manifest v2.

5. **Achado colateral BN.6: ETH 2025-H1 com w=35 dá Sharpe 2.82 vs baseline 1.21** — similar ao achado BK.1 (ns=1.25 melhor que ns=1.5). Dois sinais convergentes: pode haver otimização a fazer no eixo `(window=35, num_std=1.5)` ou `(window=30, num_std=1.25)`. **Não acionar** — data snooping. Fica registrado para Série BO se conduzida com train/val/test isolado.

## Decision

1. **Manter manifest v2 intacto em `approved_combos` e `engine.params`.** 4/8 PASS em BN está no limiar inferior da zona "médio", mas combinado com BK 4/8 o total é 8/16 = 50% sobrevivência a perturbações de 1 eixo. Não há evidência suficiente para retirar combos.

2. **Adicionar campo `robustness.window_sensitivity`** em cada combo do manifest v2 (amendment v2, sem emitir v3):
   - ETH 2024-H1 → `fragile_both`
   - ETH 2025-H1 → `fragile_low`
   - BTC 2024-H2 → `fragile_low`
   - SOL 2024-H2 → `robust`

3. **Adicionar campo derivado `robustness.cross_axis_2d`**:
   - ETH 2024-H1 → `fragile_2d` (frágil em ambos eixos)
   - ETH 2025-H1 → `semi_robust_num_std` (robusto em num_std, frágil em window)
   - BTC 2024-H2 → `fragile_2d`
   - SOL 2024-H2 → `semi_robust_window` (robusto em window, frágil em num_std)

4. **Revisar ordem de rollout paper do ADR-0032.** Hierarquia antiga (ETH 2025-H1 → ETH 2024-H1/SOL → BTC) passa a:
   - **Primeira onda paper:** ETH 2025-H1 e SOL 2024-H2 — ambos `semi_robust` em eixo diferente, diversifica o modo de falha esperado se um quebrar em live.
   - **Segunda onda (após 2+ semanas de paper sem surpresa):** BTC 2024-H2 e ETH 2024-H1 — ambos `fragile_2d`, entram com sizing reduzido (ex: 50% do notional).

5. **Hipóteses colaterais arquivadas para Série BO** (caso conduzida no futuro):
   - ETH 2025-H1 com `(window=35, num_std=1.5)` parece melhor que baseline.
   - ETH 2024-H1 com `(window=30, num_std=1.25)` parece melhor que baseline.
   - Não acionar sem design train/val/test isolado.

6. **Não abrir Série BO (perturbação de `min_width_bps`) antes de paper.** 16 pilotos em 2 eixos já deram base suficiente para rollout faseado. Abrir mais sweep pré-paper é over-engineering — Leo está sem pressa para live, mas o valor marginal do próximo sweep é baixo comparado com o valor de ver o comportamento real em paper.

## Consequences

**Prós:**
- Pareto 2D documentado empiricamente. O manifest v2 agora carrega metadata suficiente para tomar decisão informada de ordem/sizing no rollout.
- Diversificação de modo de falha na primeira onda paper (ETH 2025-H1 + SOL 2024-H2).
- Combos `fragile_2d` (ETH 2024-H1, BTC 2024-H2) marcados como "entram com sizing reduzido" — proteção explícita contra subestimar o risco.

**Contras:**
- A conclusão prática é uma redução do apetite: só 2/4 combos do manifest v2 recebem "confiança semi-robusta"; os outros 2 entram com reserva.
- O manifest v2 efetivamente vira "ETH 2025-H1 + SOL 2024-H2 como carros-chefe, BTC + ETH 2024-H1 como auxiliares com sizing reduzido". Isso muda a narrativa do ADR-0028/0029 que tratava os 4 combos como equivalentes.

**Riscos residuais:**
- Sweep cobriu apenas 2 eixos. `regime_filter.min_width_bps` e `timeframe` ainda não testados contra perturbação (Séries BO/BL futuras).
- `trades=30` como gate duro expõe BTC repetidamente — em BN.3 faltou 1 trade. Se paper mostrar BTC abaixo de 30 trades em 6 meses, o combo deve ser suspenso mesmo se performance for boa (por falta de robustez estatística).

## Follow-ups

- [ ] Atualizar `exports/approved/bollinger_width_regime_20260418_v2.json` com `robustness.window_sensitivity` + `robustness.cross_axis_2d` por combo.
- [ ] Atualizar conversa no bridge com placar e ordem de rollout revisada.
- [ ] Anexar este ADR como referência cruzada ao ADR-0028, ADR-0029, ADR-0032.
- [ ] Parar aqui pré-paper. Próxima ação = ligar paper em ETH 2025-H1 + SOL 2024-H2 (primeira onda) quando Leo quiser.

## Artefatos

- Sweep raw: `results/validation/bn-dryrun-w{25,35}-ns150-bw250-*` (8 dirs).
- Sweep summary: `exports/diag/bn_sweep_summary.json`.
- Script: `tools/run_bn_sweep.py`.
- Série brief: `agentic/active/SERIES_BN.md`.

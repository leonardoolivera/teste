# CHECKLIST.md — BK.1

- [x] pesquisa: abertura Série BK (SERIES_BK.md) + SPEC.md BK.1
- [x] implementa: reuso da engine AZ (apenas param override ns=1.25), sem código novo
- [x] valida: walk-forward 4-fold + MC 1000 + cost_stress em `results/validation/bk-dryrun-w30-ns1.25-bw250-eth-20240105_20240704/`
- [x] auditoria: ADR-0002/0019/0022/0025/0026/0030, ALL strict gates **PASS**
- [x] comparação: tabela Δ vs baseline AZ.1 (Sharpe, MDD, PnL, trades)
- [x] decisão: **PASS com folga** — libera BK.2–BK.8 em paralelo

## Resultado final BK.1 (2026-04-19 00:24 UTC)

| Métrica | Baseline AZ.1 (ns=1.5) | BK.1 (ns=1.25) | Δ |
|---|---|---|---|
| OOS trades | 38 | **41** | +8% |
| OOS Sharpe | 1.834 | **2.882** | +57% |
| OOS MDD % | 1.823% | **1.845%** | +0.02pp |
| OOS PnL % | +4.678% | **+7.235%** | +55% |
| cost_stress_ratio_min | 0.95+ | **0.9814** | PASS |
| MC p5 final_equity | — | **10252** (+2.5%) | PASS strict tail |
| MC p95 MDD | — | **3.06%** | PASS strict tail |

**Conclusão:** ns=1.25 é **MELHOR** que ns=1.5 em ETH 2024-H1. Não é degradação — é melhoria. Pareto do num_std não é pontiagudo em 1.5; pode ser largo à esquerda (mais sinais = mais captura de edge, sem perda proporcional em MDD). Precisa confirmar nos outros 3 combos via BK.2-BK.4 antes de concluir Pareto robusto vs overfit do AZ. Libera rollout BK.2-BK.8 em paralelo.

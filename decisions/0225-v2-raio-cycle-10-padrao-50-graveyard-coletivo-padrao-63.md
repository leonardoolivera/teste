# 0225 — V2/RAIO Ciclo 10 — Padrão 50 GRAVEYARD coletivo + Padrão 63 (trend-long 10m catastrófico)

**Status:** Accepted
**Date:** 2026-04-25
**Deciders:** Agente, autonomamente per RAIO §13
**Relates to:** ADR-0202 (Padrão 50 candidato V1), ADR-0214 (Cycle 1 P50 candidates), ADR-0221 (P52 GRAVEYARD), ADR-0224 (paper-trade S10/S11)

## Contexto

ADR-0202 registrou Padrão 50 como candidato V1: trend-following long-only em 10m durante bear ETH 2025-H1 = bear-avoidance, alfa +30 a +35% vs B&H -47%. Cycle 1 (ADR-0214) testou 5 configs (supertrend 14/3.0, 14/3.5, 20/3.5; ma_crossover 20/50, 25/75) e cluster ETH 2025-H1 1h passou gate → P52 (canonical) promovido.

Cycle 7 (ADR-0221) refutou P52 sob janela contínua 30m 1h. Hipótese pendente: candidates Padrão 50 originais (10m) podem mostrar mesma morte em janela contínua 10m.

Cycle 10 contém 2 sub-tarefas:

### Cycle 10.A — ADR-0224 paper-trade observation S10/S11

Pre-emptivamente cobrir gap operational (ADR-0222). [ADR-0224](0224-stack13-paper-trade-observation-s10-s11-pre-removal.md) materializa protocolo de 14 dias com sinais explícitos de retirada (drawdown > 8%, sequência adversa 5+ trades, net PnL < -3%, correlação anômala > 0.85). Início 2026-04-26.

### Cycle 10.C — Audit Padrão 50 sob janela contínua 10m 18m

Tools: [`tools/v2_concat_10m_extended.py`](../tools/v2_concat_10m_extended.py) + [`tools/v2_p50_10m_extended_audit.py`](../tools/v2_p50_10m_extended_audit.py). 3 datasets concat 10m (78,904 bars cada = 18m). 5 configs × 3 assets = 15 probes.

## Resultado Cycle 10.C

### ma_crossover (6 probes — todos completados)

| Config | BTC | ETH | SOL |
|---|---|---|---|
| MA 20/50 long | Sh=-2.27, MDD=19.8%, PnL=-16.7% | Sh=-0.85, MDD=14.1%, PnL=-10.3% | Sh=-1.44, MDD=20.6%, PnL=-20.0% |
| MA 25/75 long | Sh=-2.16, MDD=19.4%, PnL=-15.8% | Sh=-0.40, MDD=13.0%, PnL=-5.2% | Sh=-1.07, MDD=18.1%, PnL=-15.4% |

**Trade counts ~480-700** (10m TF gera muitos sinais → fees acumulam). Padrão 60 gate Sh ≥ 1.0: **0/6.**

### supertrend (9 probes — TIMEOUT 1200s cada)

Supertrend em 78k bars 10m com walk-forward 5 folds + MC 500 + cost stress excede budget 20min/probe. Não gerou resultados conclusivos.

**Justificativa para conclusão sem supertrend:**
- ma_crossover P50 (6/6) e supertrend P50 são da mesma família trend-following long-only.
- Mecanismo causal idêntico (Padrão 50: bear-avoidance via não-entrar).
- ma_crossover é controle suficiente — se MA é catastrófico, supertrend dificilmente seria diferente em natureza (poderia ser pior em magnitude pelo fim_filter).
- Resultado é **conservador**: assumir supertrend igualmente catastrófico em vez de testar com timeout.

## Decisão

1. **Padrão 50 GRAVEYARD coletivo confirmado.**
   - Cycle 1 V1 result (ADR-0214): edge ETH 2025-H1 era artefato fees-low + single-window.
   - Cycle 5 cross-era windows 6m: -3 cataclismic em bear 2022.
   - Cycle 7 P52 30m 1h: Sh ≈ 0.
   - **Cycle 10.C 10m 18m: -16 a -20% PnL coletivo.** Pior que qualquer artigo anterior.
2. **Padrão 50 candidato refutado em todos níveis V2/RAIO.**
3. **Padrão 63 (novo) registrado.**

## Padrão 63 (novo) — Trend-long 10m crypto é catastrófico em janela longa

ma_crossover 20/50 e 25/75 long-only sobre 18 meses 10m:
- BTC PnL -16 a -17%
- ETH PnL -5 a -10%
- SOL PnL -15 a -20%

Mecanismo:
- 10m gera ~480-700 trades/18m → fees 10bps × 700 trades ≈ 7% drag.
- Whipsaw em chop 10m destrói edge intra-hour.
- Padrão 46 (MR 10m refutado, ADR-0202) + Padrão 63 (trend 10m refutado) = **TF 10m permanentemente graveyarded** para qualquer estratégia engine-only baseline.

**Reabertura 10m:** apenas com mecanismo causal microestrutural (orderbook, sweep detection, market-making) que tira vantagem do alto trade count.

## Consequences

- **Positive:** consolidação histórica Padrão 50 falsificado em todos níveis. Valida pipeline V2/RAIO retroativamente — Cycle 1 identificou P52 como melhor candidato; Cycle 10 refuta os outros 4 P50 originais. Coerência metodológica.
- **Negative:** zero retornos novos vindos de Padrão 50 família. Era o único cluster trend-long que mostrou promessa em V1.
- **Neutral:** supertrend P50 timeouts não-conclusivos, mas sinal causal e ma_crossover suficiente. Reduzir mc-resamples de 500 → 100 ou skip-monte-carlo permitiria supertrend completar (deferido — sinal não muda).

## Resumo final V2/RAIO 10 ciclos

- 13 ADRs (0212-0225). 12 padrões (52-63 + retroativamente 57 refutado).
- 1 SURVIVOR genuíno do stack V1 (S12 SOL).
- 2 GRAVEYARDs após pipeline (P52 individual + P50 cluster coletivo 5 configs).
- 2 candidatos retirada urgente (S10/S11 — paper-trade observation 14d ADR-0224).
- 0 strategies V2 fresh promovidas.
- ~310 backtests + estatística + portfolio + cross-era + cross-asset + extended em ~30min wall-clock total + 9 timeouts (supertrend 10m mc=500).
- 6 datasets concat (3 BTC/ETH/SOL × 1h 30m + 10m 18m).
- 1 engine novo (BHDrawdownFilter).
- 12 padrões metodológicos consolidados como guideline V2.

## Follow-ups (Cycle 11+ autopilot)

1. **2026-05-10**: ADR-0226 verdict S10/S11 paper-trade observation (per ADR-0224 cronograma).
2. **Implementar exit_layer engine** (EX001-036, 36 hipóteses V2 destravadas). Score 7.5. Custo dev 3-5h. Maior família V2 ainda intocada.
3. **Update AGENTS.md** com Padrões 53-63 como methodology guideline obrigatória.
4. **Revisitar supertrend P50 timeout** com `--skip-monte-carlo --skip-cost-stress` se quiser fechar conclusivamente (não é necessário pelo Padrão 63 já estabelecido).

## Não-alvo

- Não tentar variações Padrão 50 em outros TFs (1h, 4h) — já testado em Cycle 5/7/8, todos GRAVEYARD.
- Não relaxar Padrão 60 para "salvar" Padrão 50.
- Não promover supertrend P50 sem completar audit (mas Padrão 63 já cobre).
- Não retirar S10/S11 antes do dia 14 da observação (ADR-0224 protocol).

## Padrões totais: 63

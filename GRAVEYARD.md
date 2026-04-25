# GRAVEYARD

**Updated:** 2026-04-25
**Protocol:** LIGHTNING_SEARCH_PROTOCOL.md (RAIO §6, §11)

> Hipóteses enterradas. Não repetir sem `reopen_exception` documentada. Imutável (append-only).

---

## V1 inheritances → GRAVEYARD

Engines refutados em V1 (ADR-0202+0211) que migram para Graveyard V2 sem novo Scout — mecanismo causal tem evidência cross-window de não funcionar:

| node_id | family | died_at_level | cause_of_death | failed_metric | do_not_repeat_reason | reopen_exception |
|---|---|---|---|---|---|---|
| V1-DON-CANONICAL | Donchian | V1 Wave 2b | 0/64 pass cross-asset/window/TF; whipsaw fatal | sharpe < 0 em todas configs | Donchian breakout 20/10 morto em 1h, 4h, 10m; dispatcher V1 confirmou 0/64 em re-run final | Reabrir só com regime detector que filtra >70% dos sinais (ADR-0202 "exigir gatilho causal novo") |
| V1-KELT-CANONICAL | Keltner | V1 Wave 2 | 1/36 pass (BTC 2025-H1 outlier) | sharpe < 1.5 em ~97% | Keltner cross-window ruído; ADR-0170-0174 + Wave 2 confirmam | Mecanismo de microstructure novo |
| V1-ZSCORE-CANONICAL | Zscore | V1 Wave 1+2 | 1/24 pass (BTC 2025-H1 outlier) | sharpe < 1.5 em ~96% | Zscore MR refutado cross-era | Regime-specific reopening com justificativa causal |
| V1-RSI-STANDALONE | RSI standalone (sem composite) | V1 Wave 1 | 0/6 pass standalone direto | sharpe < 1.5 todos | RSI sozinho não passa; sobrevive como componente do stack composite_bb_rsi | Não reabrir RSI standalone — usar dentro de ensemble |

## V2 RAIO graveyard

| node_id | family | died_at_level | cause_of_death | failed_metric | do_not_repeat_reason | reopen_exception |
|---|---|---:|---|---|---|---|
| P50-Q-001 | bear-avoidance trend ETH 2025-H1 cross-engine | 4 (RB007 fee stress) | Cross-era 2/30 + fee stress 0/10 | Sh colapsa de +2.71 (fees 5bps) → -1.51 (fees 10bps) | Padrão 50 era artefato de fees baixos + single window. ADR-0214. | Reabrir só com mecanismo causal new (não "tentar config diferente") |
| P51-001 | bollinger 15/2.0 ETH 2024-H2 | 2 (RB004 cross-era) | Cross-era 1/6 (apenas SOL 2024-H2 = Padrão 48 re-detection) | Sharpe ETH-only não generaliza | Generalização aparente foi re-detecção de P48; não é P51 | Reabrir só se mecanismo causal específico para ETH window flat for definido |
| P51-003 | bollinger 15/1.75 ETH 2024-H2 | 2 (RB004 cross-era) | Cross-era 1/6 (SOL 2024-H2 only) + fee stress 0/2 | Same as P51-001 | Mesmo perfil P51-001 | Mesma exceção P51-001 |
| P52-001-ETH-2025-H1 | ma_crossover 20/50 cross-era ETH 2025-H1 | 2 (RB004) | Sh=-1.32 ETH 2025-H1 | Cross-era ETH bear regime quebra padrão | Padrão 52 funciona em 2024-H2 regime, não em 2025-H1 bear | -- |
| (P50-001..005 ETH-2025-H1 fee stress baseline) | bear-avoidance fee fragile | 4 | Sh > 1.5 com fees 5bps mas Sh < 0 com fees 10bps | Edge era artefato de fees baixos | Padrão 53 lição (registrar): screening fees < 10bps produz falsos positivos | -- |
| **P52-Q-001** | ma_crossover 18/60 long-only canonical | 7 (janela contínua 30m) | Sh ≤ 0.87 todas configs em 30m window mesmo com bh_drawdown ótimo | Edge intra-2024-H2 (Sh=3.02) era selection bias temporal; em janela contínua 30m: Sh ≈ 0 | Padrão 60: janela curta inflaciona Sharpe via temporal selection. ADR-0221 verdict final após 7 ciclos. | Reabrir só com mecanismo causal pré-declarado para regime detectável que sustente 18m+ contínuos |
| **P50-cluster** | Padrão 50 V1 — 5 configs trend-long 10m (supertrend 14/3.0, 14/3.5, 20/3.5; ma_crossover 20/50, 25/75) | 10 (janela contínua 10m 18m) | ma_crossover 6/6 catastrófico Sh -2.27 a -0.40, PnL -5 a -20%; supertrend 9 timeouts (mc=500) mas mecanismo idêntico | Padrão 50 era bear-avoidance ETH 2025-H1 selection bias puro. Em 18m 10m: -16% a -20% PnL todos assets. Padrão 63 confirmou trend-long 10m catastrófico (fees + whipsaw). | TF 10m permanently graveyarded engine-only; reabrir só com microestrutura (orderbook, sweep detection) |
| **EX001-time-stop-MR** | EX001 V2 — time stop curto bollinger MR (ts06/12/24/48) | 1 (Scout Nível 1) | 0/15 pass Padrão 60. ts06 prejudica BTC (Sh -1.18) e ETH; ts12 marginal SOL +0.36; ts24/48 no-op. | Bollinger MR signal exit (close>=mu) é mais limpo que time stop. Time stop curto corta winners legítimos antes de mean-revert. Padrão 64. | Reabrir só com time stop **vol-aware** (ATR-scaled) ou em estratégia non-MR |
| **EX009-BE-S12-family** | EX009 V2 — BE-after-MFE em S12 standalone + cumulative S12+trail40+BE | 1 (Scout) + 5 (cumulative SOL) | Standalone SOL: Sh -47% vs raw todos triggers. Cumulative trail40+BE: Sh cai 1.37→0.78-0.93 (-32 a -41%). | Padrão 67: BE-at-entry é stop too tight pra MR crypto alta-vol; preço retraça to entry intra-reversal e força exit prematuro. Trail40 é exit dominante para MR crypto. | Reabrir só em estratégia non-MR ou em mercado de baixa vol (não crypto) |
| **LQ001-002-naive** | LQ001/LQ002 V2 — false breakout high/low + close-back-inside (sem filter) | 1 (Scout 18 probes) | 0/18 pass. BTC Sh -1.42 a -3.47, drawdowns 21-44%. ETH idem catastrófico. SOL menos pior (Sh +0.17 lookback=20) mas MDD 22%. Trade count 640-1130 → fees 10% drag. | Padrão 69: microstructure naive sem filter (volume, wick mag, HTF) gera over-trading; fees destroem edge. | Reabrir só com filter genuíno (LQ005 wick mag, LQ006 volume confirm, LQ011 magnitude+volume, LQ027 HTF align) |

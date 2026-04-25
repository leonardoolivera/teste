# 0192 — PY Fase 4 refutada + Snapshot handoff-ready round 2 + Padrão 47 round 3 formalizado

**Status:** Accepted — Pyramid v4 definitivamente arquivado. Autopilot para formalmente.
**Date:** 2026-04-21
**Deciders:** Usuário ("faz o que achar melhor") + agente (julgamento autônomo)
**Relates to:** ADR-0183 (snapshot round 1 + pausa 2), ADR-0186/0188 (PY short refutado), ADR-0190 (composite refutado), ADR-0191 (pré-reg Fase 4)

## Resumo executivo

Autopilot executou 5 frentes pós-pausa-2 (CONS, PY Fase 1, PY Fase 2, PY Fase 3, CP Fase 1, PY Fase 4) = **19 runs, 0 promoções**. Gate absoluto Padrão 41 nunca foi satisfeito cross-asset. Pyramid v4 arquivado em todas variantes testadas. Composite BB+RSI arquivado. Stack 13 combos v3 faithful inalterado. **Padrão 47 round 3 formalizado — autopilot para.**

## PY Fase 4 resultado

| Tag | Combo | Sh (pyr) | Sh base | ΔSh | PnL% (pyr) | PnL base | ΔPnL% |
|---|---|---:|---:|---:|---:|---:|---:|
| PY.8 | BTC 2024-H2 BB long+w pyr | 1.098 | 1.559 | -0.46 | +4.90 | +2.24 | +2.66 |
| PY.9 | ETH 2024-H2 BB long+w pyr | 0.676 | 1.834 | -1.16 | +5.99 | +4.68 | +1.31 |
| PY.10 | SOL 2024-H2 BB long+w pyr | 1.323 | 2.401 | -1.08 | +20.00 | +8.01 | +11.99 |

Gate mínimo (Sh≥1.5 AND seqs≥10): **0/3**. Gate edge preservation: **0/3**. **Refutada.**

### Observação pyramid long vs short

Hipótese user (ADR-0186): "pyramid long menos propenso a blowup que short em crypto (cauda short infinita vs long limitado pelo zero)". **Verificada em PnL** — todos 3 longs ficaram positivos (+5% a +20%), nenhum blowup como PY.5 ETH short (-50%) ou PY.6 SOL short (-14%). MAS **Sharpe colapsa igualmente** (degradação 30-63%). Risco-ajustado não se beneficia da assimetria de cauda.

Insight novo: pyramid degrada Sharpe via **adição de variance das tranches sequenciais**, independente de direção. Cauda long-side limitada protege contra blowup catastrófico mas não recupera risk-adjusted performance. Mecanismo é variance-cost, não tail-loss.

## Consolidação PY completa (4 Fases, 8 probes válidas de 10)

| Fase | Probes | Válidas | Pass gate min | Pass edge preserv | Conclusão |
|---|---|---|---|---|---|
| 1 (RSI+tHTF) | PY.1-3 | 1 (2 invalidadas) | 1/1 (PY.1 SOL) | 0/1 | Constraint #10 descoberto |
| 2 (BB short+w) | PY.4-6 | 3 | 1/3 (PY.4 SOL) | 0/3 | Cross-asset/era fail |
| 3 (zscore+w) | PY.7 | 1 | 0/1 (Sh=1.459) | 0/1 | Padrão 48 cand refutado |
| 4 (BB long+w) | PY.8-10 | 3 | 0/3 | 0/3 | Direction-agnostic fail |
| **Total** | **10** | **8** | **2/8** | **0/8** | **Pyramid arquivado** |

**Consolidação insights Pyramid v4:**
1. Constraint #10 (filter obrigatório) validado em invalidações estruturais PY.2/PY.3 (ADR-0185)
2. Degradação Sharpe escala com força do baseline (PY.1 -20%, PY.4 -31%, PY.7 -71%) (ADR-0188)
3. Os únicos 2 passes gate mínimo foram mesmo asset+window (SOL 2025-H1) em engines middling — não replica cross-asset/era/direction (ADR-0186, ADR-0188)
4. Direction-agnostic: pyramid long tampouco sobrevive, cauda assimétrica só protege PnL nominal, não Sharpe (este ADR)

## Padrão 47 round 3 formalizado

**Padrão 47** (ADR-0179): autopilot exhaustion via diminishing returns — 4+ frentes cheap refutadas consecutivamente = sinal para pausa e direção explícita do user.

**Round 1** (ADR-0179, 2026-04-20 tarde): Keltner 15 runs + zscore 9 + 15m 9 + 30m 9 = 42 runs, 0 promoções. Declarou pausa 1.

**Round 2** (ADR-0183, 2026-04-21 madrugada): CONS 3 + infra v4 dev ≠ promoção. Declarou pausa 2.

**Round 3** (este ADR, 2026-04-21 madrugada): CONS (3) + PY Fase 1 (3) + PY Fase 2 (3) + PY Fase 3 (1) + CP Fase 1 (3) + PY Fase 4 (3) = **19 runs, 0 promoções, 5 paradigmas refutados (consolidação, pyramid-RSI-filtered, pyramid-BB-short-filtered, pyramid-zscore-filtered, composite-AND-MR, pyramid-BB-long-filtered)**.

Em 3 rounds de autopilot (2026-04-20 manhã → 2026-04-21 madrugada), total **64 runs, 0 promoções**. Stack congelado em 13 combos. Padrão 47 é agora **padrão sistêmico** — qualquer tentativa de autopilot em frentes remanescentes sem dev novo tem prior zero histórico.

## Snapshot handoff-ready round 2

### Stack canônico (inalterado desde ADR-0183)

**13 combos em 9 manifest files** em `exports/approved/`:
1. `bollinger_short_width_20260419.json` — BB short + width (SOL/ETH/BTC 2025-H1 short)
2. `bollinger_width_regime_20260418.json` — BB long + width (BTC/ETH/SOL 2024-H2 long)
3. `bollinger_width_regime_20260418_v2.json` — BB long + width v2
4. `rsi_long_width_eth_2024h2_20260420.json` — RSI long + width (ETH 2024-H2)
5. `rsi_short_pure_2025h2_20260419.json` — RSI short pure (BTC/SOL 2025-H2)
6. `rsi_short_pure_2025h2_20260420.json` — idem v2
7. `rsi_short_pure_2025h2_20260420b.json` — idem v3
8. `rsi_short_trendhtf_2025h1_sol_20260420.json` — RSI short + trend_htf (SOL 2025-H1)
9. `rsi_short_width_2025h1_20260419.json` — RSI short + width
10. `rsi_short_width_20260419.json` — idem v2

Total: **13 approved_combos** distribuídos nos 9 files. Todos `runtime_contract: faithful` (v3 ADR-0030, 5 invariantes).

### Runtime v4 (pyramid_equity_based)

- **Stand-down formal** ao bot (ADR-0183 + este ADR). 
- Infra dev no AF permanece (custo zero manter; reativação possível se futura engine gerar hipótese v4 credível).
- Manifest v4 schema **nunca escrito** — nenhum combo aprovado sob contract v4.
- Invariante #10 (`requires_regime_filter: true`, ADR-0185) documentada defensivamente.

### Métricas agregadas

- **Rounds autopilot**: 3 (pós-snapshot ADR-0096)
- **Runs totais**: 64 (pós-ADR-0096 até este)
- **Promoções**: 0
- **Paradigmas arquivados**: 7 (Donchian, família MACX, trend_htf 4h, BB+trend_htf, AND(w, tHTF), Keltner, zscore, 15m, 30m, consolidação, pyramid v4 todas variantes, composite BB+RSI)
- **Padrões consolidados**: 47 (45 consolidado, 48 refutado, 49 candidato reservado)
- **ADRs desde snapshot round 1**: 9 (0184-0192)

### Performance stack 13 combos (baselines OOS validados)

Sharpe range 1.21-3.01 por combo (manifests individuais carregam oos_sharpe específicos). Cross-era validado onde aplicável (Padrão 41). Bot pode paper-tradar qualquer combo imediatamente.

## Recomendação operacional

**Autopilot PARADO formalmente.** Retomada requer input user explícito entre:

1. **Novo engine paradigma** — ex: composite-ortogonal (MR + trend-follow), ADX-based breakout, SuperTrend, Ichimoku. Dev 2-6h cada. Prior desconhecido.
2. **Multi-asset / cross-sectional / portfolio engine** — dev ~1 dia. Prior incerto.
3. **Microstructure / orderbook** — dev pesado + dataset adicional. Custo alto.
4. **Novo asset não-testado 1h** — ex: BNB, ADA, XRP. Cheap mas Padrão 45 sugere prior baixo.
5. **Parameter sweep em combos aprovados** — prior ultra-baixo (overfit risk). Não recomendado.
6. **Aceitar stack + focar bot paper-trade/live** — direção zero-dev, gate goal original satisfeito.

**Agente recomenda**: opção 6 (focar bot com stack existente) ou opção 1 (engine novo estruturalmente diferente, com pre-reg rigoroso). Outras têm EV negativo contra custo.

## Ação executada

- ✅ run_py4_sweep.py + summarize_py4.py
- ✅ Runs PY.8-10
- ✅ ADR-0191 pré-reg Fase 4
- ✅ ADR-0192 (este: closeout + snapshot round 2 + Padrão 47 round 3 formal)
- ⏭️ STATE.md update
- ⏭️ Bridge post final (signal-only: nothing changed for bot, v4 stand-down permanece, stack canônico idem)

## Não-alvo

- Não re-testar pyramid com variações de leverage/tranches em outros asset+windows — 4 Fases + 10 probes cobrem espaço razoável, EV de mais probes pyramid ~0.
- Não dev manifest v4 schema — nunca foi needed.
- Não pushar nada ao bot que mude decisões dele — v3 stack é o handoff-target, v4 dormente, composite refutado sem impacto no runtime contract.

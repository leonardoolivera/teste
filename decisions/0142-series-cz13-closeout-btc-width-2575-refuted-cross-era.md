# 0142 — Série CZ13 closeout: BTC width 25/75 REFUTADO cross-era, rollback candidato

**Status:** Accepted — refutação upgrade, manter 30/70 canônico
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0141 (pré-reg CZ13), ADR-0137 (CZ11), ADR-0140 (SOL trendhtf promovido), Padrão 40

## Resultado

| Tag | Janela | Regime | Tr | Sh | PnL% | MDD% |
|---|---|---|---:|---:|---:|---:|
| CZ13.1 | 2024-H1 | chop | 46 | **-0.28** | -1.06 | 6.41 |
| CZ13.2 | 2024-H2 | bull | 41 | -1.37 | -3.51 | 7.21 |

## Consolidação final cross-era (CZ10 + CZ11 + CZ13)

| Janela | Regime | Sharpe 25/75 | Sharpe 30/70 (canônico) |
|---|---|---:|---:|
| 2025-H1 | chop | **3.16** ✅ | 1.69 |
| 2025-H2 | misto | 0.45 ❌ fraco | — |
| 2024-H1 | chop | **-0.28** ❌ | — |
| 2024-H2 | bull | -1.37 (regime-incompatível) | — |

Gate ADR-0141 (2024-H1 chop regime-compatível, Sh < 0.3 → refutação) **atingido (-0.28)**.

Padrão 25 (≥2 OOS PASS regime-compatível) atinge apenas 1/2 (2025-H1 PASS, 2024-H1 FAIL, 2025-H2 fraco). **Padrão 40** (cross-era ≥1 2024 + ≥1 2025) também falha — 2024-H1 não atende Sh ≥ 1.0.

## Interpretação

BTC width 25/75 mostrou Sharpe forte apenas em **2025-H1 chop** (era-específico). Não é edge estrutural da combinação bounds extreme + filter width — é artefato de regime específico de 1 janela.

Contrasta com SOL trendhtf 25/75 (ADR-0140), que passou 3/3 regime-compatível cross-era (2024-H1, 2025-H1, 2025-H2, todos Sh ≥ 1.99). SOL trendhtf é edge real; BTC width era mirage cross-window.

## Decisão

**Manter manifest v4a `rsi_short_width_2025h1_20260419.json` em bounds 30/70 canônico.** Sem edits.

Rollback candidato: zero risco executivo pois 25/75 nunca foi promovido no manifest (SOL trendhtf foi o único que passou).

## Padrão 40 reforçado

CZ12 (SOL naked refutado) + CZ13 (BTC width refutado) = 2 confirmações consecutivas do Padrão 40. Regra agora tem evidence empírica forte:

> Upgrades de params em combos live exigem cross-era (≥1 janela 2024 + ≥1 janela 2025, Sh ≥ 1.0 em cada). 2/2 OOS "same-era" não protege contra era-dependência.

Aplicação prospectiva: CZ10 descobriu 3 candidatos upgrade (SOL naked, BTC width, SOL trendhtf); apenas 1 sobreviveu Padrão 40 (SOL trendhtf). Taxa de sobrevivência: 33%.

## Não-alvo

- Não testar bounds 35/65 em BTC (CZ10.4 já mostrou Sh 0.71 < baseline 1.69, refutado)
- Não criar manifest novo — v4a segue unchanged
- Não investigar por que 2025-H1 foi outlier — "não estruturalmente replicável" é conclusão suficiente

## Ação executada

- ✅ ADR-0141 pré-reg
- ✅ CZ13 runs (2 runs BTC 2024-H1 + 2024-H2)
- ✅ ADR-0142 closeout
- ⏳ STATE.md tarde-6 entry

## Stack pós-CZ13

13 combos inalterados. Loop CZ10-13 (sensibilidade bounds RSI) fechado:
- SOL trendhtf 25/75: **PROMOVIDO** (v6.1, ADR-0140)
- SOL naked 25/75: refutado (CZ12, ADR-0139)
- BTC width 25/75: refutado (CZ13, este ADR)

# 0147 — Série CZ15 closeout: SOL short BB ns=2.0 REFUTADO cross-window, Padrão 41 validado

**Status:** Accepted — refutação upgrade, `num_std=1.5` canônico preservado. Padrão 41 empiricamente validado.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0145 (CZ14), ADR-0146 (pré-reg), Padrão 40, Padrão 41

## Resultado

| Tag | Janela | Regime | Tr | Sh | PnL% | MDD% |
|---|---|---|---:|---:|---:|---:|
| CZ15.1 | 2025-H2 | misto | 66 | **0.01** | -0.22 | 9.64 |
| CZ15.2 | 2024-H1 | chop | 69 | **0.46** | 2.62 | 10.18 |
| CZ15.3 | 2024-H2 | bull (ignorar) | 71 | 1.27 | 5.89 | 4.45 |

## Consolidação cross-window (CZ14 + CZ15)

| Janela | Regime | Sh ns=2.0 | Regime-compat? | PASS ≥ 1.5? |
|---|---|---:|:---:|:---:|
| 2025-H1 | chop | **4.94** | sim | ✅ |
| 2025-H2 | misto | 0.01 | sim | ❌ |
| 2024-H1 | chop | 0.46 | sim | ❌ |
| 2024-H2 | bull | 1.27 | não | n/a |

**Regime-compatível PASS: 1/3.** Gate ADR-0146 exigia ≥3/4 (ou ≥2/3 regime-compatível novas). **Refutação.**

## Interpretação

CZ14.2 foi outlier puro de 2025-H1 chop. Nenhuma das outras duas janelas regime-compatível replicou (0.01 e 0.46 são baixíssimos). `num_std=1.5` canônico permanece ótimo para família Bollinger short.

2024-H2 bull Sh=1.27 é curiosidade — short genérico em bull tipicamente negativo, mas aqui filter width 300 bps deve ter excluído maior parte do bull trend forte. Não muda decisão.

## Padrão 41 validado

Predição: "1/N forte + resto fails = asset/janela-specific, não param-specific".
CZ14: 1/6 (SOL short 2025-H1) vs 5 fails.
CZ15: janela-specific confirmado (0/2 regime-compatível replica).

Padrão 41 agora tem evidence empírica clean: screening com alta variância prevê corretamente refutação cross-window.

## Decisão

- **Não editar** `bollinger_short_width_20260419.json` (mantém ns=1.5)
- **Não editar** `bollinger_width_regime_20260418_v2.json` (mantém ns=1.5)
- Bridge **não postado** (nada mudou pro bot — signal-only)
- Arquivar hipótese Bollinger num_std extremo

## Comparação com RSI 25/75 (CZ10-13 análogo)

| Série | Screening | Cross-window/era | Verdict final |
|---|---|---|---|
| RSI 25/75 | 3/3 PASS (param-specific) | 1/3 sobreviveu Padrão 40 | SOL trendhtf promovido |
| BB ns=2.0 | 1/6 PASS (janela-specific) | 0/2 regime-compat replicou | Arquivado |

Taxa de sobrevivência: RSI 33% (1/3), BB 0%. Padrão 41 previu corretamente que variância de screening antecipa falha cross-window.

## Ação executada

- ✅ ADR-0146 pré-reg
- ✅ CZ15 runs (3 runs)
- ✅ ADR-0147 closeout
- ✅ Padrão 41 validado empiricamente
- ⏳ STATE.md tarde-8 entry

## Não-alvo

- Não re-testar ns=2.0 em outras combinações (5/6 fails já refutaram param-specific)
- Não investigar 2024-H2 bull Sh=1.27 (janela única, regime-incompatível)
- Não criar manifest novo

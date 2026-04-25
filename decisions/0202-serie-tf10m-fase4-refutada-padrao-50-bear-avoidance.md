# 0202 — Série TF10m Fase 4 refutada + Padrão 50 candidato: trend-following bear-avoidance 10m

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Usuário ("testa outras coisas no 10 min") + agente
**Relates to:** ADR-0201 (pré-reg Fase 4), ADR-0200 (MR 10m exauridamente refutada), ADR-0008 (ma_crossover), ADR-0011 (donchian), ADR-0193 (supertrend)

## Contexto

Após MR 10m exauridamente refutada em 3 Fases (5 engines × 66 probes, 4/66 pass todos em SOL 2024-H2 regime window), testei 3 non-MR strategies em 10m: ma_crossover, donchian, supertrend. 27 probes (9 × 3 blocos).

## Resultado (27/27 completos)

### Bloco I — ma_crossover 20/50 long 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% | B&H% | alfa% |
|---|---|---:|---:|---:|---:|---:|
| TF10I.1 | BTC 2024-H2 | 232 | -0.30 | -0.95 | +70 | -35.95 |
| TF10I.2 | ETH 2024-H2 | 228 | -0.71 | -2.57 | 0 | -2.57 |
| TF10I.3 | SOL 2024-H2 | 243 | -1.79 | -7.88 | +46 | -30.88 |
| TF10I.4 | BTC 2025-H1 | 249 | -1.64 | -4.41 | -8 | -0.41 |
| **TF10I.5** | **ETH 2025-H1** | **228** | **+1.61** | **+6.75** | **-47** | **+30.25** |
| TF10I.6 | SOL 2025-H1 | 222 | +0.85 | +3.94 | -40 | +23.94 |
| TF10I.7 | BTC 2025-H2 | 220 | -0.47 | -1.07 | +12 | -7.07 |
| TF10I.8 | ETH 2025-H2 | 247 | -2.06 | -6.99 | +70 | -41.99 |
| TF10I.9 | SOL 2025-H2 | 234 | -1.03 | -4.33 | +35 | -21.83 |

**1/9 pass (TF10I.5).** Alfa real de +30% vs B&H em ETH bear H1 2025.

### Bloco J — donchian 20/10 long 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% | B&H% |
|---|---|---:|---:|---:|---:|
| TF10J.1 | BTC 2024-H2 | 464 | -4.91 | -11.13 | +70 |
| TF10J.2 | ETH 2024-H2 | 441 | -2.07 | -5.97 | 0 |
| TF10J.3 | SOL 2024-H2 | 472 | -3.96 | -13.90 | +46 |
| TF10J.4 | BTC 2025-H1 | 458 | -2.71 | -6.13 | -8 |
| TF10J.5 | ETH 2025-H1 | 442 | -0.34 | -1.51 | -47 |
| TF10J.6 | SOL 2025-H1 | 464 | -2.14 | -9.36 | -40 |
| TF10J.7 | BTC 2025-H2 | 465 | -6.12 | -11.41 | +12 |
| TF10J.8 | ETH 2025-H2 | 448 | -2.55 | -7.71 | +70 |
| TF10J.9 | SOL 2025-H2 | 464 | -2.05 | -7.08 | +35 |

**0/9 pass.** Donchian 20/10 em 10m é catastrófico — trade count ~450/probe cria whipsaws destrutivos. Todas probes negativas. Donchian breakout não sobrevive 10m.

### Bloco K — supertrend atr=10 mult=3.0 bi 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% | B&H% |
|---|---|---:|---:|---:|---:|
| TF10K.1 | BTC 2024-H2 | 556 | -3.94 | -14.66 | +70 |
| TF10K.2 | ETH 2024-H2 | 508 | -2.31 | -10.94 | 0 |
| TF10K.3 | SOL 2024-H2 | 551 | -4.34 | -24.90 | +46 |
| TF10K.4 | BTC 2025-H1 | 583 | -2.68 | -9.75 | -8 |
| TF10K.5 | ETH 2025-H1 | 508 | +1.04 | +5.88 | -47 |
| TF10K.6 | SOL 2025-H1 | 515 | +0.94 | +5.99 | -40 |
| TF10K.7 | BTC 2025-H2 | 633 | -3.34 | -11.23 | +12 |
| TF10K.8 | ETH 2025-H2 | 557 | -1.00 | -5.59 | +70 |
| TF10K.9 | SOL 2025-H2 | 567 | -0.78 | -5.17 | +35 |

**0/9 pass Sharpe gate.** Mas TF10K.5 / K.6 positivos em bear H1 2025 (alfa ~+26-29% vs B&H) — padrão similar a ma_crossover.

## Agregado Fase 4

- **Total Sharpe pass: 1/27** — abaixo gate 2/27. **Refutado por bloco e agregado.**
- **Total alfa pass (alfa > 0 e Sh≥1.5): 1/27** — único TF10I.5.

## Achado-chave: Padrão 50 candidato — trend-following bear-avoidance 10m

**Observação cruzada blocos I + K (ambos trend-following)**:

| Probe | TF10I (ma_crossover) | TF10K (supertrend) |
|---|---|---|
| ETH 2025-H1 (bear -47%) | Sh=+1.61, +30% alfa ✓ | Sh=+1.04, +29% alfa ✓ |
| SOL 2025-H1 (bear -40%) | Sh=+0.85, +24% alfa ✓ | Sh=+0.94, +26% alfa ✓ |
| BTC 2025-H1 (bear -8%) | Sh=-1.64, alfa -0.4% | Sh=-2.68, alfa -6% |
| Outros (bull/flat) | Todos Sh<0, alfa<<0 | Todos Sh<0, alfa<<0 |

**Padrão 50 candidato**: **trend-following long-only em 10m durante bear markets alt (ETH/SOL) gera alfa positiva vs B&H por não-entrada** (evita drawdown por ficar flat). Não em BTC (magnitude bear muito menor, -8% não cria o bear-friendly regime).

Valor: **diagnóstico**, não operacional diretamente. Para operacionalizar seria necessário:
1. Regime detection (ex: ATR expansion, macro trend) para escolher quando alocar.
2. Validação cross-era: H1 2025 foi um cycle específico; outros bears podem ter vol/structure diferente.
3. Teste de risk-adjusted return vs cash (não entrar é aproximadamente equivalente a ficar em cash rendendo 0%).

**Prior de promoção**: BAIXO. Dois sinais, uma única window (H1 2025), dois engines correlacionados (MA crossover e supertrend são ambos momentum-long). Não é 2 peças independentes de evidência — é **uma evidência regime-specific observada por 2 lentes**. Padrão 48 logic (regime trumps engine) aplica.

## Decisão

1. **TF10m Fase 4 refutado** (gate agregado 1/27 < 2/27; gate por bloco 0-1/9 todos fail).
2. **Frente TF10m cobertura total exaurida**: 8 engines × 66+27 = **93 probes totais**. 5 engines MR (BB, RSI, zscore, Keltner, composite) + 3 non-MR (ma_crossover, donchian, supertrend). Alpha_forge engines ao todo = 8 (+ dummy). Cobertura ≡ 100%.
3. **Padrão 46 definitivo**: MR 10m refutado cross-window cross-asset cross-engine.
4. **Padrão 50 candidato** registrado (não promovido): trend-following long-only 10m = bear-avoidance em alts regime-specific. Sem cross-era validation, sem operacionalização.
5. **Padrão 48 consolidado** permanece (SOL 2024-H2 = MR-friendly regime window).
6. **Donchian 10m definitivamente morto**: 0/9 todas catastróficas, -6 worst Sharpe, trade overfit fatal.
7. **Supertrend 10m definitivamente morto** como standalone (0/9 gate Sh), mas parte do Padrão 50 candidato para regime bear alt.
8. **Stack 13 combos v3 inalterado**. Nenhum export, nenhum manifest.
9. **Frente TF10m fechada definitivamente**. Infra preservada para eventual uso futuro.
10. **Autopilot**: não retoma. Frentes residuais remanescem: portfolio cross-sectional, microstructure, paper-trading prolongado, stress adversarial, regime detection (nova frente motivada pela cauda Padrão 48+50).

## Agregado final TF10m (4 Fases)

| Fase | Engines | Probes | Pass Sh | Pass alfa | Nota |
|---|---|---:|---:|---:|---|
| 1 | BB+width short | 9 | 1 | - | SOL 2024-H2 regime |
| 2 | BB/RSI × long/short/width/trend_htf | 30 | 2 | - | ambos SOL 2024-H2 |
| 3 | zscore/Keltner/composite | 27 | 1 | - | SOL 2024-H2 (composite) |
| 4 | ma_crossover/donchian/supertrend | 27 | 1 | 1 | ETH 2025-H1 bear-avoidance |
| **Total** | **8 engines** | **93** | **5** | **1** | **5.4% Sh rate ≈ noise floor** |

**Cobertura efetiva TF10m**: 5/93 Sharpe pass (5.4% ≈ null rate). **1/93 alfa pass** (TF10I.5). Não há nenhum engine que passe gate ≥2/9 em QUALQUER bloco. Frente TF10m **refutada exaustivamente** em todos engines disponíveis.

## Não-alvo

- Não testar variações de parâmetro das 8 engines em 10m (prior ~0 dado cobertura exaustiva).
- Não promover TF10I.5 (1 probe isolado, regime-specific, não cross-era validated).
- Não abrir frente regime detection sem user approval (mudança de escopo significativa).
- Não ir para 5m/1m (prior ~0 mantido).

## Total padrões: 49 (46 escopo final; 48 consolidado; 50 candidato; 49 composite-MR absorvido em 46).

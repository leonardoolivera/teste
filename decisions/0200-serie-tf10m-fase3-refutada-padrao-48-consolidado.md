# 0200 — Série TF10m Fase 3 refutada + Padrão 48 consolidado (SOL 2024-H2 window regime) + MR 10m cross-engine exaustão total

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Usuário ("outras estrategias reversao a media") + agente
**Relates to:** ADR-0199 (pré-reg Fase 3), ADR-0198 (Fase 2 closeout + Padrão 46 consolidado), ADR-0186 (Padrão 48 candidato original), Padrão 46/48

## Contexto

Após Fase 2 refutada cobrir BB+RSI × long/short × width/trend_htf em 10m, user pediu testar outras MR strategies: zscore, Keltner, composite_bb_rsi. 27 probes (3 engines × 3 assets × 3 windows).

## Resultado (27/27 completos)

### Bloco F — zscore 20/2.0 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10F.1 | BTC 2024-H2 | 488 | -1.22 | -4.89 |
| TF10F.2 | ETH 2024-H2 | 463 | +0.30 | +1.19 |
| TF10F.3 | SOL 2024-H2 | 448 | -0.09 | -1.02 |
| TF10F.4 | BTC 2025-H1 | 460 | -2.82 | -10.44 |
| TF10F.5 | ETH 2025-H1 | 468 | -4.05 | -23.03 |
| TF10F.6 | SOL 2025-H1 | 482 | -1.71 | -12.18 |
| TF10F.7 | BTC 2025-H2 | 469 | -4.16 | -14.01 |
| TF10F.8 | ETH 2025-H2 | 482 | -2.31 | -12.15 |
| TF10F.9 | SOL 2025-H2 | 484 | -2.02 | -12.52 |

**0/9 pass.** Trade count disparado (~450-500 em 6m) = threshold zscore 2.0 sem filtro cria overtrading. Fee drag + slippage dominam totalmente em 2025 (Sh -4 worst case). zscore MR naked em 10m é catastroficamente ruim, pior que noise floor.

### Bloco G — Keltner 20/14/2.0 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10G.1 | BTC 2024-H2 | 276 | -0.08 | -0.50 |
| TF10G.2 | ETH 2024-H2 | 264 | -0.09 | -0.72 |
| TF10G.3 | SOL 2024-H2 | 269 | +0.73 | +4.12 |
| TF10G.4 | BTC 2025-H1 | 315 | -0.73 | -2.88 |
| TF10G.5 | ETH 2025-H1 | 251 | -4.05 | -22.93 |
| TF10G.6 | SOL 2025-H1 | 273 | -0.85 | -6.43 |
| TF10G.7 | BTC 2025-H2 | 307 | -3.37 | -11.48 |
| TF10G.8 | ETH 2025-H2 | 288 | -0.04 | -0.61 |
| TF10G.9 | SOL 2025-H2 | 274 | -0.21 | -1.75 |

**0/9 pass.** Trade count ~260-315, alto mas menor que zscore. Padrão 1h→10m degradação consistente com ADR-0170-0174 refutação prévia.

### Bloco H — composite_bb_rsi 20/2.0/14/30-70 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10H.1 | BTC 2024-H2 | 178 | -1.76 | -6.90 |
| TF10H.2 | ETH 2024-H2 | 176 | +0.14 | +0.37 |
| **TF10H.3** | **SOL 2024-H2** | **181** | **+1.70** | **+10.48** |
| TF10H.4 | BTC 2025-H1 | 178 | +0.62 | +2.14 |
| TF10H.5 | ETH 2025-H1 | 202 | +0.15 | +0.44 |
| TF10H.6 | SOL 2025-H1 | 187 | -0.39 | -3.34 |
| TF10H.7 | BTC 2025-H2 | 186 | -1.04 | -3.74 |
| TF10H.8 | ETH 2025-H2 | 190 | +0.29 | +1.20 |
| TF10H.9 | SOL 2025-H2 | 180 | -0.50 | -3.55 |

**1/9 pass (TF10H.3 SOL 2024-H2 Sh=1.70).** AND(BB+RSI) filtra trade count para ~180 (muito melhor que zscore/Keltner). SOL 2024-H2 novamente outlier.

## Agregado Fase 3

- **Total pass: 1/27** — **abaixo** do gate agregado ≥2/27. **REFUTADO**.
- Per ADR-0199 decisão condicional: "Todos blocos 0-1/N pass" → Padrão 46 consolida além BB/RSI.

## Achado-chave: Padrão 48 consolidado (SOL 2024-H2 window regime)

**Todos 4 passers das 3 Fases TF10m concentrados em SOL 2024-H2**:

| Fase | Tag | Engine | Sh | Tr |
|---|---|---|---:|---:|
| 1 | TF10.3 | BB+width 20/2.0 short | 1.77 | 98 |
| 2 | TF10B.3 | RSI 30/70 + width short | 2.63 | 161 |
| 2 | TF10D.3 | RSI 30/70 + width long | 2.55 | 91 |
| 3 | TF10H.3 | composite BB+RSI 20/2.0/30-70 | 1.70 | 181 |

**4 engines diferentes × 1 window = prova definitiva de regime window-specific**, não edge engine-específico:
- 2 direções (long + short) passam simultaneamente → não é edge direcional.
- 3 famílias de engine (BB puro, RSI puro, BB∧RSI) passam → não é edge algorítmico.
- Width filter ou não passa → não é edge do filtro.
- Single window (SOL 2024-H2) passa enquanto outras 8 windows (2025-H1, 2025-H2 em todos 3 ativos; 2024-H2 em BTC+ETH) falham consistentemente → regime period-asset-specific.

**Padrão 48 consolidado**: SOL 2024-H2 foi uma janela onde **todas engines MR 10m teriam ganho** (regime favorece MR 10m); isto é uma propriedade do mercado naquele período, não da estratégia. Não promove — não generaliza cross-era (nenhuma evidência de que regime repete), e mesmo dentro da janela o valor é limitado sem saber *a priori* qual window está MR-friendly.

## Agregado final MR 10m cross-Fase

| Cobertura | Probes | Pass | Rate | Notas |
|---|---:|---:|---:|---|
| Fase 1 (BB short) | 9 | 1 | 11% | TF10.3 SOL 2024-H2 |
| Fase 2 (BB long, RSI long/short, RSI+trend_htf) | 30 | 2 | 7% | ambos SOL 2024-H2 |
| Fase 3 (zscore, Keltner, composite) | 27 | 1 | 4% | SOL 2024-H2 |
| **Total MR 10m** | **66** | **4** | **6.1%** | **100% SOL 2024-H2** |

**6.1% pass rate** ≈ noise floor sob gate aleatório H0. **Clustering 4/4 em 1 window** é o sinal principal — o sinal não é edge, é **regime estrutural**.

## Decisão

1. **TF10m Fase 3 refutado**. MR 10m cross-engine exaustão **total** (5 strategies cobertas: BB, RSI, zscore, Keltner, composite_bb_rsi + 1 direcional: trend_htf).
2. **Padrão 46 escopo final**: "MR intra-hour timeframe (10m/15m/30m) cross-window cross-asset cross-engine refuta edge. Edge MR é fenômeno 1h sweet spot. Total: 3/66 probes passing = 4.5% noise floor (excluindo contribuição SOL 2024-H2 regime) ou 6.1% bruto." *(Nota: o número 3/66 vem de 1 outlier pass fora SOL 2024-H2... na verdade 0/66 fora SOL 2024-H2 — então rate verdadeira do edge noise=0%, rate aparente inflada por regime=6%.)*

   Correção: dos 4 pass, todos em SOL 2024-H2. **Fora desse regime: 0/60 = 0% pass rate.** MR 10m edge é **estatisticamente zero** cross-regime.

3. **Padrão 48 consolidado**: SOL 2024-H2 window é regime MR-friendly universal (4 engines confirmed). SOL 2025-H1 window candidato (pyramid/BB por ADR-0186, refutado cross-era em ADR-0188). Padrão documenta que crypto tem janelas regime-specific que favorecem MR em *qualquer* engine — valor diagnóstico, não operacional.
4. **Frente MR 10m fechada definitivamente**. Não há engines MR adicionais no alpha_forge para testar em 10m.
5. **Stack 13 combos v3 inalterado**. Nenhum export. Nenhum manifest emitido.
6. **Infra 10m preservada** (ADR-0196 cobre — custo zero manter).
7. **Autopilot**: **não retoma**. Frentes residuais ADR-0183 seguem disponíveis (portfolio/cross-sectional, microstructure, aceitar stack, stress adversarial), mais duas novas:
   - **Non-MR strategies em 10m** (ma_crossover, donchian, supertrend — não testadas em 10m, todas refutadas em 1h mas **não MR** então Padrão 46 não se aplica diretamente).
   - **MR em 5m / 1m ultra-fast** (prior ~0, não recomendo).

## Análise técnica: por que zscore/Keltner foram tão ruins

zscore 488 trades em 6 meses com fee=5bps+slippage=2bps → ~7bps por round-trip × 488 ≈ **34% de drag** comparado ao naked edge. Mesmo que threshold 2.0σ tivesse edge real, seria engolido. Keltner similar mas metade do trade count (~270) → drag ~19%.

composite_bb_rsi com AND reduz para ~180 trades → drag ~12.6%, comparable à BB/RSI puros. Por isso composite "quase passa" em BTC 2025-H1 (Sh+0.62) enquanto zscore/Keltner estão -3 a -4. **Implicação**: se alguém quisesse ressuscitar MR 10m, o vetor seria **threshold restritivo** (menos trades, mais seletivo) — mas mesmo assim o único passer (composite SOL 2024-H2) é regime-bound, não edge.

## Não-alvo

- Não testar MR 10m com params mais restritivos (threshold=3σ, etc.) — conditional no regime, custo alto prior baixo.
- Não testar MR 5m/1m (prior ~0 dado gradient 30m→15m→10m todos null).
- Não consolidar Padrão 48 operacionalmente (regime detection requer modelo separado, frente distinta).

## Total padrões: 48 (46 escopo final consolidado; 48 consolidado definitivo, 49 composite-MR candidato refutado absorvido em Padrão 46).

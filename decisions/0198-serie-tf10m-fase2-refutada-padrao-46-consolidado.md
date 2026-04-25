# 0198 — Série TF10m Fase 2 refutada + Padrão 46 consolidado totalmente (intra-hour cover completo) + SOL 2024-H2 window regime

**Status:** Accepted
**Date:** 2026-04-21
**Deciders:** Usuário + agente
**Relates to:** ADR-0197 (pré-reg Fase 2), ADR-0195/0196 (Fase 1 TF10m + Padrão 46 extendido), Padrão 45 (outlier isolado), Padrão 48 candidato (SOL 2025-H1 pyramid)

## Contexto

Após ADR-0197 pré-reg 30 probes Fase 2 (4 blocos cobrindo engines canônicas restantes do stack em 10m): RSI+width short (B, 9), BB+width long (C, 9), RSI+width long (D, 9), RSI+trend_htf short SOL (E, 3). Gate por bloco ≥2/9 (≥1/3 para E), gate agregado ≥2/30.

## Resultado (30/30 completos)

### Bloco B — RSI+width short 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10B.1 | BTC 2024-H2 | 46 | -0.71 | -0.95 |
| TF10B.2 | ETH 2024-H2 | 91 | -0.83 | -1.42 |
| **TF10B.3** | **SOL 2024-H2** | **161** | **2.63** | **+7.92** |
| TF10B.4 | BTC 2025-H1 | 40 | -2.01 | -2.43 |
| TF10B.5 | ETH 2025-H1 | 129 | -2.08 | -6.00 |
| TF10B.6 | SOL 2025-H1 | 168 | -0.65 | -2.97 |
| TF10B.7 | BTC 2025-H2 | 29 | -0.57 | -0.88 |
| TF10B.8 | ETH 2025-H2 | 98 | -1.61 | -4.06 |
| TF10B.9 | SOL 2025-H2 | 140 | -2.98 | -8.97 |

**1/9 pass (TF10B.3 SOL 2024-H2).** Gate bloco FAIL (<2/9).

### Bloco C — BB+width long 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10C.1 | BTC 2024-H2 | 25 | 1.44 | +1.16 |
| TF10C.2 | ETH 2024-H2 | 28 | 0.95 | +1.12 |
| TF10C.3 | SOL 2024-H2 | 61 | 0.96 | +2.04 |
| TF10C.4 | BTC 2025-H1 | 16 | -0.87 | -0.71 |
| TF10C.5 | ETH 2025-H1 | 36 | -1.54 | -2.93 |
| TF10C.6 | SOL 2025-H1 | 75 | -1.89 | -4.71 |
| TF10C.7 | BTC 2025-H2 | 13 | -0.48 | -0.70 |
| TF10C.8 | ETH 2025-H2 | 40 | -2.28 | -4.59 |
| TF10C.9 | SOL 2025-H2 | 62 | -1.59 | -4.07 |

**0/9 pass.** Gate bloco FAIL.

### Bloco D — RSI+width long 10m (9 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10D.1 | BTC 2024-H2 | 31 | 0.66 | +0.65 |
| TF10D.2 | ETH 2024-H2 | 48 | -0.90 | -1.05 |
| **TF10D.3** | **SOL 2024-H2** | **91** | **2.55** | **+5.32** |
| TF10D.4 | BTC 2025-H1 | 17 | 0.56 | +0.45 |
| TF10D.5 | ETH 2025-H1 | 61 | -1.42 | -2.72 |
| TF10D.6 | SOL 2025-H1 | 91 | 1.00 | +2.52 |
| TF10D.7 | BTC 2025-H2 | 20 | -0.57 | -0.82 |
| TF10D.8 | ETH 2025-H2 | 49 | -1.45 | -2.99 |
| TF10D.9 | SOL 2025-H2 | 68 | -1.98 | -4.51 |

**1/9 pass (TF10D.3 SOL 2024-H2).** Gate bloco FAIL.

### Bloco E — RSI+trend_htf short SOL 10m (3 probes)

| Tag | Combo | Tr | Sh | PnL% |
|---|---|---:|---:|---:|
| TF10E.1 | SOL 2024-H2 | 118 | 0.81 | +2.93 |
| TF10E.2 | SOL 2025-H1 | 143 | 0.93 | +4.39 |
| TF10E.3 | SOL 2025-H2 | 169 | -0.13 | -0.88 |

**0/3 pass.** Gate bloco FAIL.

## Agregado Fase 2

- **Total pass: 2/30** (TF10B.3 SOL 2024-H2 Sh=2.63, TF10D.3 SOL 2024-H2 Sh=2.55).
- Gate agregado ≥2/30: **atingido tecnicamente** mas **0 blocos individuais passam** (todos 0-1/N).
- Per ADR-0197 decisão condicional: cenário "Todos blocos 0-1/N pass" → **Padrão 46 consolida totalmente**.

## Achado-chave: SOL 2024-H2 é regime window-specific

Ambos passers Fase 2 + TF10.3 Fase 1 = **3 engines diferentes passando na mesma window (SOL 2024-H2)**:

| Tag | Engine | Sh | Tr |
|---|---|---:|---:|
| TF10.3 | BB+width 20/2.0 short | 1.77 | 98 |
| TF10B.3 | RSI 30/70 + width short | 2.63 | 161 |
| TF10D.3 | RSI 30/70 + width long | 2.55 | 91 |

**3 engines × 1 window** é evidência de **regime window-specific**, não edge engine-específico. SOL 2024-H2 apresentou volatilidade realizada + consolidações frequentes de curto prazo que 10m captura (timing-específico) e essa dinâmica favorece MR em ambas direções (long e short) simultaneamente — sinal claro de regime, não de sinal preditivo.

Formalizado como **Padrão 48-extension** (já existente Padrão 48 candidato em ADR-0186 cobrindo SOL 2025-H1 regime pyramid/BB-friendly; agora documentado SOL 2024-H2 regime MR-10m-friendly). **NÃO promove** — prior de que regime persiste out-of-window é baixíssimo (ADR-0176 já mostrou decay cross-era zscore; ADR-0188 refutou Padrão 48 candidato SOL 2025-H1 pyramid cross-era).

## Decisão

### Consolidação Padrão 46 total intra-hour

**Cobertura completa 10m/15m/30m × todas engines MR do stack**:

| TF | Engines testadas | Probes | Pass | Pass rate |
|---|---|---:|---:|---:|
| 30m | BB+width short | 9 | 0 | 0% |
| 15m | BB+width short | 9 | 0 | 0% |
| 10m | BB+width short (Fase 1) | 9 | 1 | 11% |
| 10m | RSI+width short (Fase 2 B) | 9 | 1 | 11% |
| 10m | BB+width long (Fase 2 C) | 9 | 0 | 0% |
| 10m | RSI+width long (Fase 2 D) | 9 | 1 | 11% |
| 10m | RSI+trend_htf short SOL (Fase 2 E) | 3 | 0 | 0% |
| **Total** | | **57** | **3** | **5.3%** |

**5.3% pass rate** ≈ noise floor sob gate `Sh≥1.5 AND N≥30` (H0 aleatório prediz ~2-5%). Todos 3 passers concentrados em **SOL 2024-H2** reforça regime-effect, não edge. **Padrão 46 consolidado TOTALMENTE**: MR intra-hour em crypto é refutado cross-window cross-asset cross-engine.

### Ações

1. **TF10m Fase 2 refutado**. Frente "timeframes intra-hour" fechada definitivamente.
2. **Padrão 46 atualizado**: escopo final "MR intra-hour timeframe (10m/15m/30m) cross-engine refuta edge. Edge BB/RSI MR em crypto é fenômeno de 1h sweet spot".
3. **Padrão 48 candidato expandido**: SOL 2024-H2 regime MR-10m-friendly (3 engines, 1 window) — **não promover**, registrado para referência futura se aparecer nova hipótese SOL-window específica.
4. **Stack 13 combos inalterado**. Nenhum export, nenhum manifest v7 emitido.
5. **Infra 10m preservada** (ADR-0196 já cobria — custo zero manter).
6. **Autopilot**: **não retoma**. Este foi redirect user pós-Fase-1 ("testa em todas as outras") — cobertura agora completa. Próxima frente requer input user.
7. **Não testar 5m/1m**: prior ~0 dado gradiente 30m→15m→10m todos refutados e 3 passers concentrados em regime window.

## Opções residuais (ADR-0183 + redirect)

Frentes não exploradas que o user pode invocar:
- Portfolio/cross-sectional (combinar stack combos em carteira).
- Microstructure (orderbook, funding rates, basis — requer dados não-OHLCV).
- Aceitar stack 13 combos, passar para validação paper-trading prolongada.
- Walk-forward stress em cenários adversariais (dados faltantes, gaps, latência simulada).

## Não-alvo

- Não rodar mais variações TF10m engine-params (prior ~0 dado 3/39 concentrados em 1 window).
- Não investigar SOL 2024-H2 regime isoladamente (não generaliza, custo ≥ 9 runs com prior baixo).
- Não regressar TF15m/TF30m com engines Fase 2 (mesmo raciocínio: prior baixíssimo dado noise floor já estabelecido).

## Total padrões: 48 (46 consolidado totalmente, 48 expandido cobrindo 2 SOL windows candidatos, 49 candidato composite-MR pendente).

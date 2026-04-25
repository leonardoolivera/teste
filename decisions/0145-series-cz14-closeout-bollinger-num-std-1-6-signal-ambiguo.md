# 0145 — Série CZ14 closeout: Bollinger num_std 1/6 outlier (SOL short ns=2.0), signal ambíguo

**Status:** Accepted — screening: 1 outlier forte, 5 fails. Não abre cross-window direto por gate.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0144 (pré-reg), Padrão 38 (RSI 25/75 análogo), Padrão 40 (cross-era)

## Resultado

| Tag | Combo | Janela | ns | Tr | Sh | Lift vs 1.5 | PnL% |
|---|---|---|---:|---:|---:|---:|---:|
| CZ14.1 | SOL short w20 | 2025-H1 | 1.2 | 124 | 0.89 | -1.82 | 5.21 |
| CZ14.2 | SOL short w20 | 2025-H1 | 2.0 | 82 | **4.94** | **+2.23** ⭐ | 33.84 |
| CZ14.3 | ETH short w20 | 2025-H1 | 1.2 | 92 | 0.76 | -1.64 | 3.44 |
| CZ14.4 | ETH short w20 | 2025-H1 | 2.0 | 57 | 0.62 | -1.78 | 2.81 |
| CZ14.5 | SOL long w30 | 2024-H2 | 1.2 | 57 | 2.32 | -0.08 | 7.57 |
| CZ14.6 | SOL long w30 | 2024-H2 | 2.0 | 40 | 1.55 | -0.85 | 4.68 |

## Avaliação gate

Gate ADR-0144 pre-registrado:
- Upgrade candidato: ≥2/6 runs com lift > 0.5 → abrir CZ15 cross-window
- Signal ambíguo: 1/6 com lift > 0.5 → documentar outlier, não seguir
- Refutação screening: 0/6 com lift ≥ 0.5 → `num_std=1.5` ótimo local

**Resultado: 1/6 atinge gate upgrade (CZ14.2 SOL short ns=2.0 +2.23). Signal ambíguo pelo gate literal.**

## Interpretação

SOL short w=20 ns=2.0 em 2025-H1 é outlier forte (Sh quase dobrou: 2.71 → 4.94). PnL 33.84% em 6 meses, 82 trades — volume razoável. Mas todos os outros 5 runs falharam (incluindo ns=1.2 no mesmo combo, que caiu pra Sh=0.89).

Três hipóteses para o outlier CZ14.2:
1. **Edge genuíno** asset-regime-param específico (SOL short em chop 2025-H1 responde a bandas largas ns=2.0). Seria análogo ao que aconteceu com RSI 25/75 SOL trendhtf (passou 3/3 cross-era em ADR-0140).
2. **Artefato de janela única** — outra era refutaria (análogo BTC width 25/75 em CZ13).
3. **Interação bandas × filter width** — bandas Bollinger largas (ns=2.0) + filter width min=300 bps selecionam regime pouco volátil de forma específica, amplificando edge em SOL 2025-H1.

Hipóteses 1 e 2 são indistinguíveis sem cross-window/cross-era. Dado que RSI 25/75 teve taxa de sobrevivência 1/3 após Padrão 40, prior está ~30% para hipótese 1.

## Decisão

**Não abrir CZ15 automaticamente.** Gate "ambíguo" (1/6) bloqueia cross-window por pre-registro. Documento outlier e deixo decisão explícita pro usuário:

- **Opção A**: abrir CZ15 SOL short w=20 ns=2.0 cross-window (2025-H2 + 2024-H1 + 2024-H2) como análogo CZ11+CZ12. 3 runs. Se 2/3 regime-compatível Sh ≥ 1.5, promove.
- **Opção B**: arquivar como curiosidade. SOL short em manifest live (bollinger_short_width_20260419) já tem Sh=2.71 com canônico ns=1.5; 4.94 seria lift ~2x Sharpe, mas 1/6 isolado é fraco epistemicamente.
- **Opção C**: tratar como refutação (5/6 fail). `num_std=1.5` é ótimo local para Bollinger em geral, exceto outlier SOL short 2025-H1.

## Padrão 41 (NOVO, metodológico)

**"Screening primeira-janela com alta variância entre combos (ex: 1/N forte + (N-1)/N fails) deve ser tratado como signal ambíguo, não upgrade. Disciplina Padrão 40 exige cross-era antes de promover, mas screening com variância deve exigir também cross-combo validation: se 1 combo dispara e 2+ similares não, prior é 'asset-specific' ou 'janela-specific', não 'param-specific'."**

Aplicação:
- CZ14: SOL short ns=2.0 Sh=4.94 isolado, mesmo SOL long no mesmo asset (CZ14.6) caiu. Param-specific hipótese enfraquecida.
- Contraste RSI CZ10: 3/3 dispararam com 25/75 (todos combos independentes do filter), prior param-specific forte.

## Ação executada

- ✅ ADR-0144 pré-reg
- ✅ CZ14 runs (6 runs)
- ✅ ADR-0145 closeout
- ✅ Padrão 41 formalizado
- ⏳ Decisão A/B/C aguardando usuário
- ⏳ STATE.md tarde-7 entry

## Não-alvo

- Não editar bollinger manifests (nenhum promoção sem cross-window)
- Não abrir CZ15 sem autorização explícita
- Não re-testar ns=2.0 em combos onde já falhou

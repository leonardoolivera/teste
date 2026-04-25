# 0146 — Série CZ15 pré-registro: SOL short Bollinger ns=2.0 cross-window + cross-era

**Status:** Pre-registered
**Date:** 2026-04-20
**Deciders:** Usuário ("o que vc achar melhor") + agente (escolheu A)
**Relates to:** ADR-0145 (CZ14 closeout, 1/6 outlier), Padrão 40 (cross-era), Padrão 41 (variância de screening)

## Motivação

CZ14.2 outlier: SOL short w=20 ns=2.0 2025-H1 Sh=4.94 (vs 2.71 canônico ns=1.5). Padrão 41 sugere hipótese asset/janela-específica. Testar se edge sobrevive cross-window e cross-era antes de decidir.

Risco: Padrão 41 prevê falha — outlier não-replicável seria consistente com 5/6 fails da CZ14.

## Escopo

3 runs SOL short Bollinger w=20 ns=2.0 + filter width(300) em janelas não-testadas:

| Tag | Janela | Regime | Regime-compatível? |
|---|---|---|:---:|
| CZ15.1 | 2025-H2 | misto | sim |
| CZ15.2 | 2024-H1 | chop pré-bull | sim |
| CZ15.3 | 2024-H2 | bull | **não** (short contra trend) |

## Gate pré-registrado (Padrão 40 estrito)

Agregado CZ14 + CZ15 (4 janelas total):

- **Promoção autorizada**: ≥3/4 regime-compatível Sh ≥ 1.5 (2025-H1 já PASS Sh=4.94; precisa 2/2 ou 3/3 das novas regime-compatíveis). 2024-H2 bull ignorado por Padrão 26.
- **Staging ambíguo**: 2/3 regime-compatível PASS → documentar sem promover, aguardar janela extra
- **Refutação**: <2/3 regime-compatível PASS → outlier CZ14.2 é era-específico, `num_std=1.5` canônico preservado. Padrão 41 empiricamente validado.

## Não-alvo

- Não testar ETH ou SOL long ns=2.0 (CZ14.4/14.6 já falharam — 5/6 pattern é evidência contra param-specific)
- Não variar filter width (fixar 300 bps como CZ14.2)
- Não variar window (fixar 20)
- Não promover sem atingir gate estrito

Timebox: ~4min. Closeout em ADR-0147.

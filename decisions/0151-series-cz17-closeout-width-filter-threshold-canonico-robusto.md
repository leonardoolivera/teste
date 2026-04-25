# 0151 — Série CZ17 closeout: width filter threshold 0/6 refutação, canônicos 250/300 robustos

**Status:** Accepted — refutação screening. Canônicos 250/300 preservados. Padrão 42 expandido.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0150 (pré-reg), ADR-0149 (CZ16 window), Padrão 42 (ótimo local), Padrão 41

## Resultado

| Tag | Combo | bps | Tr | Sh | Lift vs canônico | PnL% |
|---|---|---:|---:|---:|---:|---:|
| CZ17.1 | SOL short | 150 | 126 | 2.18 | -0.53 | 15.30 |
| CZ17.2 | SOL short | 500 | 68 | 2.22 | -0.49 | 10.48 |
| CZ17.3 | ETH short | 150 | 125 | 2.45 | +0.05 | 14.62 |
| CZ17.4 | ETH short | 500 | 46 | 1.99 | -0.41 | 7.03 |
| CZ17.5 | SOL long | 125 | 66 | 1.61 | -0.79 | 5.80 |
| CZ17.6 | SOL long | 400 | 23 | 1.26 | -1.14 | 3.05 |

Maior lift: ETH short bps=150 (+0.05, efetivamente igual ao canônico).

## Avaliação gate

Gate ADR-0150:
- Upgrade convergente: ≥2/6 lift > 0.5 → CZ18
- Signal divergente: 1/6 lift > 0.5 → Padrão 41 bloqueia
- Refutação screening: 0/6 lift ≥ 0.5 → canônicos robustos

**0/6 atinge. Refutação screening.**

## Interpretação

Filter threshold tem sensibilidade mais **achatada** que engine params (CZ16 window). Todos 6 alternativos mantêm Sh 1.26-2.45 (positivos), mas canônicos 250/300 são levemente superiores em 5/6 casos.

Dois padrões:

1. **Threshold baixo (150/125)**: ~2× mais trades (126 vs 82 SOL short baseline; 125 vs 57 ETH; 66 vs 40 SOL long). Captura regimes marginalmente voláteis, dilui sinal com low-vol noise. Sh cai ligeiramente mas não quebra.
2. **Threshold alto (500/400)**: ~metade dos trades (68 vs 82; 46 vs 57; 23 vs 40). Seletividade excessiva, perde oportunidades reais. Sh cai mais em SOL long (1.26 com 23 trades) — sample pequeno degrada walk-forward.

Canônicos (300 short / 250 long) são sweet spot empírico já validado.

## Padrão 42 expandido

Original Padrão 42 (ADR-0149): engine window tem ótimo local ~15-30.

**Corolário (ADR-0151)**: filter `min_width_bps` também tem ótimo local, mas com **superfície mais plana** — alternativos degradam suavemente (-0.4 a -1.0), não colapsam como window rápido (-1.87). Isso implica:

> Filter thresholds têm tolerância de ~±50% antes de lift cair abaixo de 0.5 unidades de Sharpe. Engine params são mais sensíveis. Priorizar exploração de engine knobs em screenings futuros; filter thresholds são segunda ordem.

Implicação prática: quando procurar por edge via sensibilidade, engine params (bounds, window) pagam mais que filter params. Ordenação prospectiva: (1) bounds engine, (2) window engine, (3) filter threshold, (4) filter internal params.

## Decisão

- Manter todos manifests com thresholds canônicos (300 short / 250 long)
- Nenhuma edição
- Bridge **não postado**

## Consolidação screening Bollinger (CZ14+CZ16+CZ17)

| Knob | Screening | Padrão ativado |
|---|---|---|
| num_std | 1/6 divergente → CZ15 refutou | 41 validado |
| window | 0/6 refutação | 42 original |
| min_width_bps | 0/6 refutação | 42 expandido (corolário) |

Bollinger family totalmente sensibilizada. Nenhum upgrade candidato sobrevivente. Canônicos (w=20/30, ns=1.5, bps=300/250) são ótimos locais robustos.

## Ação executada

- ✅ ADR-0150 pré-reg
- ✅ CZ17 runs (6 runs)
- ✅ ADR-0151 closeout
- ✅ Padrão 42 expandido com corolário
- ⏳ STATE.md tarde-10 entry

## Não-alvo

- Não testar threshold extremos (< 100 ou > 600) — superfície plana não compensa
- Não variar filter internal params (window=30, num_std=1.5) — segunda ordem
- Não abrir cross-window (gate bloqueia)

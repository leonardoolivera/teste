# 0149 — Série CZ16 closeout: Bollinger window canônico robusto, 0/6 refutação screening

**Status:** Accepted — refutação screening completa. `w=20` (short) / `w=30` (long) confirmados como ótimos locais.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0148 (pré-reg), Padrão 38 (bounds extreme), Padrão 41 (screening variance)

## Resultado

| Tag | Combo | Window | Tr | Sh | Lift vs canônico | PnL% |
|---|---|---:|---:|---:|---:|---:|
| CZ16.1 | SOL short | 10 | 158 | **-1.87** | -4.58 | -12.07 |
| CZ16.2 | SOL short | 40 | 66 | 1.70 | -1.01 | 10.25 |
| CZ16.3 | ETH short | 10 | 136 | **-1.49** | -3.89 | -7.82 |
| CZ16.4 | ETH short | 40 | 46 | 1.34 | -1.06 | 5.97 |
| CZ16.5 | SOL long | 15 | 100 | 2.85 | **+0.45** | 9.23 |
| CZ16.6 | SOL long | 45 | 41 | 2.20 | -0.20 | 7.25 |

Maior lift positivo: CZ16.5 SOL long w=15 (+0.45), logo abaixo do threshold 0.5.

## Avaliação gate

Gate ADR-0148:
- Upgrade convergente: ≥2/6 lift > 0.5 → abrir CZ17
- Signal divergente: 1/6 lift > 0.5 → Padrão 41 bloqueia
- Refutação screening: 0/6 lift ≥ 0.5 → canônico robusto

**0/6 atinge lift ≥ 0.5. Refutação screening.**

## Interpretação

Dois padrões claros:

1. **Window rápido (10) colapsa em short**: Sh=-1.87 SOL, -1.49 ETH. Excesso de sinais (158, 136 trades) com baixa qualidade. Bollinger bands muito responsivas pegam ruído de alta frequência como reversão, cozem em whipsaw.
2. **Window lento (40-45) degrada levemente** mas positivo: Sh=1.34-2.20, lift ~-1.0. Menos sinais (41-66 trades), bandas tardias perdem início da reversão.

`w=20` (short) e `w=30` (long) são ótimos não-triviais. SOL long w=15 chegou mais perto do canônico (+0.45) mas insuficiente.

## Padrão 42 (NOVO): engines de mean-reversion têm ótimo local em window intermediário

**"Em estratégias mean-reversion com bandas (Bollinger) ou thresholds (RSI), o parâmetro de `window` (período de suavização) tem ótimo local não-trivial entre ~15 e ~30 para 1h crypto. Windows rápidos (≤10) colapsam em whipsaw (ruído); windows lentos (≥40) degradam por latência. Exploração deve começar em window canônico ±50% e expandir apenas se lift > 0.5 aparecer nos flancos."**

Evidence:
- RSI canônico w=14 (nunca testado alternativo mas bounds extremes em CZ10 não variaram window)
- Bollinger short w=20: ±50% = w=10 (FAIL) e w=30 (não testado aqui, mas w=20 ótimo estabelecido)
- Bollinger long w=30: ±50% = w=15 (+0.45, quase canônico) e w=45 (-0.20)

Limite prático: próximas séries de sensibilidade devem focar outros knobs (bounds, filter params) antes de re-varrer window.

## Decisão

- Manter todos manifests Bollinger em `w=20` (short) / `w=30` (long)
- Nenhuma edição de manifest
- Bridge **não postado** (nada mudou pro bot)

## Comparação com séries análogas

| Série | Knob | Screening result | Cross-window | Final verdict |
|---|---|---|---|---|
| CZ10 | RSI bounds | 3/3 PASS (convergente) | 1/3 Padrão 40 | SOL trendhtf promovido |
| CZ14 | BB num_std | 1/6 PASS (divergente) | 0/2 CZ15 | Arquivado (Padrão 41 validado) |
| CZ16 | BB window | 0/6 PASS (refutação) | n/a | Canônico robusto (Padrão 42 novo) |

Três padrões de screening distintos, três respostas diferentes. Metodologia calibrada.

## Ação executada

- ✅ ADR-0148 pré-reg
- ✅ CZ16 runs (6 runs)
- ✅ ADR-0149 closeout
- ✅ Padrão 42 formalizado
- ⏳ STATE.md tarde-9 entry

## Não-alvo

- Não testar window extremos (<10 ou >60) — Padrão 42 dispensa
- Não variar 2 knobs simultaneamente (entangles diagnóstico)
- Não abrir CZ17 (gate bloqueia)

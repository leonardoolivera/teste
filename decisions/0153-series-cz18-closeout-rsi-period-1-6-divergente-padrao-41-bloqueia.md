# 0153 — Série CZ18 closeout: RSI period 1/6 divergente, Padrão 41 bloqueia upgrade

**Status:** Accepted — signal divergente, arquivar. Padrão 41 aplicado. BTC width p=21 outlier registrado.
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0152 (pré-reg), ADR-0147 (CZ15 precedente), Padrão 41 (divergence)

## Resultado

| Tag | Combo | period | Tr | Sh | Lift | PnL% |
|---|---|---:|---:|---:|---:|---:|
| CZ18.1 | SOL naked 30/70 | 7 | 216 | 0.76 | -1.54 | 4.20 |
| CZ18.2 | SOL naked 30/70 | 21 | 48 | 1.82 | -0.48 | 10.56 |
| CZ18.3 | BTC width 30/70 | 7 | 64 | **-2.76** 💥 | -4.45 | -7.09 |
| CZ18.4 | BTC width 30/70 | 21 | 32 | **3.62** ⭐ | +1.93 | 8.71 |
| CZ18.5 | SOL trendhtf 25/75 | 7 | 87 | -0.03 | -2.03 | -0.51 |
| CZ18.6 | SOL trendhtf 25/75 | 21 | 11 | -0.92 | -2.92 | -4.35 |

**1/6 atinge gate upgrade (CZ18.4 BTC width p=21: +1.93).** 5 fails, 1 com colapso profundo (p=7 BTC, Sh=-2.76).

## Avaliação gate

Gate ADR-0152:
- Upgrade convergente: ≥2/6 lift > 0.5 → CZ19
- Signal divergente: 1/6 lift > 0.5 → Padrão 41 bloqueia
- Refutação screening: 0/6 lift ≥ 0.5

**1/6 → signal divergente. Padrão 41 aplica (precedente CZ14/CZ15).**

## Interpretação

Dois achados:

### 1. RSI period=7 é destrutivo (Padrão 42 validado cross-família)

p=7 em BTC width: Sh=-2.76 (PnL -7.09%). p=7 SOL trendhtf: Sh=-0.03 (zero). p=7 SOL naked: Sh=0.76 (colapso suave). 3/3 runs p=7 pioram significativamente vs canônico.

RSI responde igual ao Bollinger (CZ16 w=10): period rápido amplifica ruído em mean-reversion 1h crypto. Padrão 42 generaliza cross-família (BB e RSI ambos têm ótimo local window intermediário).

### 2. BTC width p=21 Sh=3.62 é outlier forte mas isolado

Lift +1.93 é magnitude grande (análogo ao CZ14.2 SOL short ns=2.0 com +2.23). Mas padrão igual: isolado, outros combos com mesmo knob (SOL naked p=21: lift -0.48; SOL trendhtf p=21: lift -2.92) não replicam.

Padrão 41 prevê falha cross-window. Decisão: **não abrir CZ19 cross-window por gate pre-registrado**.

### 3. SOL trendhtf p=21 com 11 trades: sample colapsado

Apenas 11 trades em 6 meses (0.06 trades/dia). Filter trend_htf + RSI p=21 lento + bounds 25/75 é 3 filtros empilhados restritivos — produz sample insuficiente para walk-forward confiável. Nota metodológica: combos já filtered são sensíveis a slowing engine params.

## Decisão

- Não editar manifests — todos permanecem p=14 canônico
- Bridge **não postado**
- BTC width p=21 outlier arquivado com referência explícita — se usuário quiser testar cross-window futuramente (override Padrão 41), abrir ADR dedicado

## Padrão 42 validação cross-família

| Família | Knob | Fast | Canônico | Slow |
|---|---|---|---|---|
| Bollinger (CZ16) | window | 10: Sh=-1.87 | 20: 2.71 | 40: 1.70 |
| RSI (CZ18) | period | 7: Sh=-2.76 | 14: 1.69 | 21: 3.62* |

Ambas mean-reversion: period/window rápido colapsa. RSI mostra asimetria interessante (p=21 lento levantou em BTC) que BB não mostrou — pode ser que RSI lento acumula mais sinais qualitativos em regime-filtered data. Mas apenas 1/3 combos → não generaliza.

## Padrão 41 confirmado 3x

Precedentes:
- CZ14.2: 1/6 SOL short BB ns=2.0 (+2.23) → CZ15 refutou cross-window
- CZ18.4: 1/6 BTC width RSI p=21 (+1.93) → Padrão 41 preventivo, não abre cross-window

Regra consolidada: **1/N com lift grande + resto fails = asset/janela-específico; prior empírico forte contra promoção, não vale custo de CZ19 de 3 runs**.

Se usuário discordar e quiser testar BTC width p=21 cross-window (análogo CZ15), pode abrir override explícito. Default: Padrão 41 governa.

## Ação executada

- ✅ ADR-0152 pré-reg
- ✅ CZ18 runs (6 runs)
- ✅ ADR-0153 closeout
- ✅ Padrão 42 validado cross-família (BB + RSI)
- ✅ Padrão 41 aplicado preventivamente (3ª vez)
- ⏳ STATE.md tarde-11 entry

## Não-alvo

- Não testar period extremos (< 5 ou > 30)
- Não abrir CZ19 automaticamente (Padrão 41 bloqueia)
- Não re-testar p=7 em outros combos (3/3 colapso já refuta)

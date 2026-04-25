# 0115 — Série CT closeout: 4h cross-timeframe RSI short (SOL replica, BTC misto)

**Status:** Accepted — resultado informativo, sem promoção ao stack
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0114 (pré-registro)

## Resultado (3 runs RSI short 4h)

| Tag | Combo baseline (1h) | 1h Sh | 4h Trades | 4h Sh | 4h PnL% | Verdict |
|---|---|---:|---:|---:|---:|---|
| CT.1 | v4a BTC 2025-H1 short+width | 1.69 | 17 | 0.77 | +2.41 | replicação fraca |
| CT.2 | v8.1 BTC 2025-H2 short naked | 1.64 | 16 | **-0.43** | -1.34 | **refutação** |
| CT.3 | v8.1 SOL 2025-H2 short naked | 2.30 | 23 | **2.81** | +16.31 | **replicação forte** |

## Interpretação

**SOL 2025-H2 RSI short replica extraordinariamente bem em 4h** — Sh=2.81 > baseline 1h 2.30. Edge SOL short em crypto 2025-H2 é estruturalmente robusto cross-timeframe.

**BTC 2025-H1 short+width** fraco mas positivo em 4h. Width filter pode estar ajudando menos em 4h (menor fração de barras filtradas por resolução mais grosseira).

**BTC 2025-H2 short naked** FALHA em 4h. Mesma janela/engine que funciona em 1h gera Sh=-0.43 em 4h. Edge timeframe-específico.

## Decisão

**Não promover nada ao stack ativo nesta série.** Probe exploratória cumpriu função. Observações:

1. Cross-timeframe **não é universal** — depende de ativo (SOL > BTC em 2025-H2)
2. Sample size em 4h é pequeno (16-23 trades por 6 meses) — promoção a live exigiria 2+ janelas PASS e gate trades≥30 relaxado apenas sob protocolo dedicado
3. SOL 4h resultado é **hook pra série dedicada**: testar SOL RSI short 4h em 2024-H2 (validação cross-window dentro de 4h timeframe)

## Padrão 28 (NOVO): cross-timeframe replica é ativo-específica, não engine-específica

CT demonstra: mesmo engine (RSI(14/30/70) short naked) na mesma janela (2025-H2), em ativos diferentes (BTC vs SOL), produz resultados opostos em 4h (FAIL vs PASS forte). Cross-timeframe não é propriedade do engine — é propriedade da interação engine × ativo × timeframe.

Implicação: expansão de timeframe requer validação **por ativo**, não extrapolação "engine X funciona em 4h porque funciona em 1h".

## Follow-up aberto (não promovido)

Hipótese para série CU futura: **SOL RSI short 4h cross-window** (testar 2025-H1 e 2024-H2). Se ambos Sh≥0.5 → candidato genuíno a manifest paralelo v9-4h.

Não abrir série CU agora (usuário pediu depois item 3 nova family).

## Não-alvo

- Não alterar manifests existentes — CT é probe, não auditoria de combos ativos
- Não mudar live_status de combos 1h — estes continuam validados no seu timeframe
- Não emitir bridge post — zero mudança operacional

## Stack pós-CT

13 combos inalterados. Métricas:
- Evidência acumulada: RSI short 1h válido; 4h funciona em SOL mas não em BTC 2025-H2
- Backlog: "SOL 4h cross-window series" (opt-in futuro)

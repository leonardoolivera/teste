# 0137 — Série CZ11 closeout: RSI 25/75 cross-window confirma 2/3 combos, BTC width não

**Status:** Accepted — 2 promoções pendentes autorização explícita do usuário (mudança real de manifest)
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0136 (pré-reg), ADR-0135 (CZ10 candidato), Padrões 25/26/38

## Resultado consolidado (CZ10 + CZ11)

### SOL naked 25/75

| Janela | Regime | Sh | Verdict |
|---|---|---:|---|
| 2025-H2 misto (CZ10.1) | misto | **3.61** | strict |
| 2024-H2 bull (CZ11.1) | bull | -1.71 | FAIL (Padrão 26 esperado) |
| 2025-H1 chop (CZ11.2) | chop | **1.52** | strict |

**Regime-compatível: 2/2 PASS strict.** Promoção autorizada pelo gate.

### BTC width 25/75

| Janela | Regime | Sh | Verdict |
|---|---|---:|---|
| 2025-H1 chop (CZ10.3) | chop | **3.16** | strict |
| 2024-H2 bull (CZ11.3) | bull | -1.37 | FAIL (esperado) |
| 2025-H2 misto (CZ11.4) | misto | 0.45 | fraco/contextual |

**Regime-compatível: 1 strict + 1 fraco.** Cross-window não confirma magnitude do upgrade. NÃO promove.

### SOL trendhtf 25/75

| Janela | Regime | Sh | Verdict |
|---|---|---:|---|
| 2025-H1 chop (CZ10.5) | chop | **2.00** | strict |
| 2024-H2 bull (CZ11.5) | bull | -0.19 | filter contém |
| 2025-H2 misto (CZ11.6) | misto | **3.36** | strict |

**Regime-compatível: 2/2 PASS strict.** Promoção autorizada pelo gate.

## Decisão técnica vs decisão produção

**Decisão técnica (gate atendido):**
1. SOL naked: atualizar manifest 30/70 → 25/75 (Sharpe esperado 2.30 → ~2.5+ baseado em 2 janelas)
2. SOL trendhtf: atualizar manifest 30/70 → 25/75 (Sharpe esperado 0.89 → ~2.7 baseado em 2 janelas)
3. BTC width: manter 30/70 (cross-window inconclusivo)

**Decisão produção: PENDENTE autorização explícita do usuário.**

Mudar params de combo aprovado é **mudança real de estratégia em produção** — diferente de rodar sweep. Bridge signal-only (memória feedback_bridge_signal_only) define que mudança em manifest aprovado é evento que muda decisão do bot, então requer:
1. Autorização explícita do usuário pra editar manifests aprovados
2. ADR de promoção dedicado (se autorizado)
3. Bridge post para bot informando mudança de params + nova versão manifest
4. Recalibração paper-trade no bot com novos bounds

## Padrão 39 (NOVO): regime-compatible cross-window strict é gate suficiente para promoção

Quando combo passa em 2/2 janelas regime-compatível com Sh ≥ 1.0 + delta vs baseline ≥ +0.5 (CZ10 magnitude), o gate Padrão 25 está atendido com folga e promoção é tecnicamente justificada. FAIL em janela regime-oposto não conta como refutação se mecanismo Padrão 26 está documentado (short em bull, long em chop, etc.).

Limitação: gate técnico ≠ autorização produção — mudança em manifest aprovado é decisão do usuário, não do agente.

## Próximos passos imediatos

**Aguardando decisão do usuário:**
- Opção A: autorizar promoção SOL naked + SOL trendhtf para 25/75 → eu edito manifests + ADR promoção + bridge post
- Opção B: manter staging-only, registrar achado, não mudar produção
- Opção C: pedir mais janelas (ex: SOL naked em 2024-H1 quando dataset existir) antes de promover

## Padrão 38 confirmado

Bounds 25/75 dominante em RSI short crypto 1h confirmado em 2 dos 3 combos top. BTC width é exceção — possível razão: filter width já reduz universo, bounds extreme em cima reduz demais a sample em 2025-H2.

## Ação executada

- ✅ ADR-0137 closeout (este)
- ✅ Série CZ11 documentada
- ✅ STATE.md entry (consolidado tarde-3)
- ⏳ Decisão pendente do usuário sobre promoção produção

## Não-alvo

- Não editar manifests sem autorização explícita
- Não emitir bridge post sem decisão de promoção
- Não mudar 13 combos count

## Stack pós-CZ11

13 combos inalterados. Achado: 2 combos (SOL naked + SOL trendhtf) **podem ter Sharpe ~2× upgrade** se autorizada mudança 30/70 → 25/75.

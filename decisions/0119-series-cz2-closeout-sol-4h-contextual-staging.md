# 0119 — Série CZ2 closeout: SOL RSI short 4h cross-window (contextual, staging)

**Status:** Accepted — staging/contextual, não promoção automática
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0118 (pré-registro), ADR-0115 (CT.3 baseline), Padrão 25/26/28

## Resultado agregado (3 janelas SOL 4h)

| Tag | Janela | Regime | Trades | Sharpe | PnL% | Verdict |
|---|---|---|---:|---:|---:|---|
| CT.3 | 2025-H2 | misto | 23 | **2.81** | +16.31 | strict |
| CZ2.2 | 2025-H1 | chop | 17 | 0.64 | +3.63 | contextual |
| CZ2.1 | 2024-H2 | bull | 13 | **-1.31** | -7.42 | FAIL |

**2/3 PASS (1 strict + 1 contextual), 1 FAIL em bull regime-oposto.**

## Interpretação

Padrão 26 (ADR-0108): FAIL em regime direcionalmente oposto (short em bull sem filter direcional) é **estrutural-esperado**, não window-specific fluke. Mesma lógica do CZE vs CZF.

Evidência válida cross-window: 2 janelas regime-compatíveis (2025-H2 misto + 2025-H1 chop) com Sh ≥ 0.5. Atende gate contextual (Padrão 25 refinado, ADR-0109).

## Decisão

**Staging/contextual, NÃO promoção a stack ativo.**

Racional:
1. Gate pré-registrado (ADR-0118) exigia ≥2/3 Sh ≥ 1.0 pra abrir manifest v9-4h → **1/3 strict apenas**
2. Trade counts 4h baixos (13-23) — menor poder estatístico que 1h (51 trades v6, 92 v8.1)
3. Alpha em 4h é diferido (cada trade pesa mais, vol de PnL é maior)

Candidato staging significa: combo documentado + ADR com evidência, mas **NÃO entra em live** até:
- 3ª janela PASS strict (ex: 2024-H1 chop) OU
- Cross-window evidence com filter direcional (trend_htf short_only em 4h) OU
- Decisão explícita do usuário pra promoção sob protocolo relaxado

## Padrão 30 (NOVO): 4h cross-window sob sample-constraint

Crypto 4h timeframe produz ~1/4 dos trades de 1h em mesma janela. Gates pré-registrados originais (trades≥30, MC p5>9500) são **mal-calibrados** para 4h.

Proposta futura se quisermos considerar 4h seriamente:
- Gate trades≥15 em 4h (proxy equivalente a 30 em 1h)
- Gate MC p5>9200 em 4h (relaxar 300bp por menor n)
- Exigir cross-window replicação mesmo em contextual

Não formalizar como politica geral ainda — decidir caso-a-caso conforme mais evidência 4h acumule.

## Follow-up aberto (não agendado)

Hipóteses futuras se retomar SOL 4h:
1. **SOL 4h 2024-H1**: testar em chop pré-bull (análogo a CZF) pra elevar contextual → strict
2. **SOL 4h + trend_htf**: replicar v6 pattern em 4h (trend_htf no contexto 4h seria 16h ou 1d)
3. **Cross-asset 4h**: BTC/ETH em 4h (CT.2 mostrou BTC 2025-H2 4h FAIL, mas CT.1 BTC 2025-H1+width fraco positivo)

Não abrir nenhum automaticamente.

## Ação executada

- ✅ ADR-0119 closeout (este documento)
- ✅ Série CZ2 documentada
- ✅ STATE.md entry

## Não-alvo

- Não criar manifest v9-4h (gate não atendido)
- Não alterar stack (zero combos adicionados/removidos)
- Não emitir bridge post (nada muda operacionalmente)

## Stack pós-CZ2

13 combos inalterados. Registro: "SOL RSI short 4h é candidato staging contextual, 2/3 janelas PASS, promoção requer evidence adicional".

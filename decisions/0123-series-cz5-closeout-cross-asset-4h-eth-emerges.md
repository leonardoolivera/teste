# 0123 — Série CZ5 closeout: ETH 4h emerge como segundo ativo replicador, BTC 4h sepultado

**Status:** Accepted — ETH 4h staging (não promoção), BTC 4h matriz negativa fechada
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0122 (pré-registro), ADR-0115 (CT closeout), Padrão 26, Padrão 28

## Resultado

| Tag | Asset | Janela | Regime | Tr | Sh | Verdict |
|---|---|---|---|---:|---:|---|
| CZ5.1 | BTC | 2024-H2 | bull | 14 | **-3.18** | FAIL |
| CZ5.2 | ETH | 2024-H2 | bull | 11 | **-3.02** | FAIL (regime-esperado) |
| CZ5.3 | ETH | 2025-H1 | chop | 26 | **2.16** | **strict** |
| CZ5.4 | ETH | 2025-H2 | misto | 22 | 0.59 | contextual |

## BTC 4h: matriz fechada negativa

Combinando CT.1-CT.2 + CZ5.1, BTC 4h RSI short é **3/3 não-replica**:
- BTC 4h 2024-H2 naked: -3.18 FAIL
- BTC 4h 2025-H1 width: 0.77 fraca
- BTC 4h 2025-H2 naked: -0.43 FAIL

**Conclusão**: BTC RSI short é edge 1h-específico (v4a 1.69, v8.1 1.64 baseline 1h) que **não transporta para 4h** em nenhuma janela. Reforço empírico do Padrão 28.

## ETH 4h: cross-asset replicador novo

ETH 4h regime-compatível: 2/2 PASS (1 strict + 1 contextual). FAIL em bull-2024-H2 é Padrão 26 estrutural-esperado (igual SOL CZ2.1).

ETH 2025-H1 chop: Sh=2.16, 26 trades, MDD=6.31% — **mais forte que SOL CZ2.2** (0.64) na mesma janela e regime. ETH 2025-H2 misto: 0.59, similar a SOL CZ2.2.

## Decisão

**ETH 4h RSI short = staging single-asset.** Mesmo critério aplicado a SOL CZ2: não promoção a stack ativo, mas combo documentado.

Racional:
1. Gate pré-registrado pedia 2/3 Sh≥1.0 ETH → só 1/3 strict
2. ETH 2025-H1 isolado (1 strict, 1 contextual, 1 FAIL bull) é evidence equivalente ao staging SOL CZ2 — não inferior, mas também não suficiente pra promoção
3. **Coincidência interessante**: SOL e ETH ambos têm strict em 2025-H2 e 2025-H1 misto/chop respectivamente. Sugere que o regime macro 2025 tem propriedade que favorece RSI short 4h em altcoins, não em BTC.

## Padrão 32 (NOVO): split BTC vs altcoin em RSI short 4h

Em 4h, RSI short replica em **altcoins (SOL, ETH)** mas não em BTC. Hipótese: BTC 4h tem características estatísticas diferentes (menor vol relativa, micro-estrutura mais eficiente em higher timeframes) que neutralizam edge do oversold-rebound classic.

Implicação prática:
- Não rastrear BTC 4h pra extensões de RSI short (matriz fechada)
- Próximas extensões 4h focar em altcoin universe (LINK 4h? AVAX 4h? — não disponível, exigiria infra)
- Manter BTC 4h apenas pra replicação de combos width/regime (CT.1 mostrou que com filter melhora marginalmente)

## Próximo passo possível (não agendado)

ETH 4h staging poderia ser elevado se:
1. ETH 4h 2024-H1 chop (não disponível — mesmo gap que SOL)
2. ETH 4h 2025-H1 + filter regime (bollinger_width) replicar pattern v4a/v7

## Ação executada

- ✅ ADR-0123 closeout
- ✅ Série CZ5 documentada
- ✅ STATE.md entry (consolidado CZ4+CZ5+CZ6)

## Não-alvo

- Não promover ETH 4h ao stack (mesmo critério SOL CZ2)
- Não criar manifest v9-4h
- Não alterar stack

## Stack pós-CZ5

13 combos inalterados. Registry adicional: ETH RSI short 4h é candidato staging contextual (par com SOL).

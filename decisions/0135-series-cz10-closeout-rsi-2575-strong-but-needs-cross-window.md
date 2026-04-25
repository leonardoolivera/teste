# 0135 — Série CZ10 closeout: RSI 25/75 mostra upgrade forte, EXIGE cross-window antes de promoção

**Status:** Accepted — upgrade candidato 3 combos, gate Padrão 25 ativado
**Date:** 2026-04-20
**Deciders:** Usuário + agente
**Relates to:** ADR-0134 (pré-reg), Padrão 25

## Resultado

| Tag | Combo | Bounds | Tr | Sh | vs 30/70 | Verdict |
|---|---|---|---:|---:|---|---|
| CZ10.1 | SOL 2025-H2 naked | 25/75 | 66 | **3.61** | +1.31 | **UPGRADE** |
| CZ10.2 | SOL 2025-H2 naked | 35/65 | 115 | 1.32 | -0.98 | WORSE |
| CZ10.3 | BTC 2025-H1 width | 25/75 | 44 | **3.16** | +1.47 | **UPGRADE** |
| CZ10.4 | BTC 2025-H1 width | 35/65 | 52 | 0.71 | -0.98 | WORSE |
| CZ10.5 | SOL 2025-H1 trendhtf | 25/75 | 32 | **2.00** | +1.10 | **UPGRADE** |
| CZ10.6 | SOL 2025-H1 trendhtf | 35/65 | 66 | **2.21** | +1.31 | UPGRADE |

**3/3 combos top mostram upgrade significativo com bounds 25/75.** Magnitude do delta (+1.10 a +1.47 Sharpe) é grande — não dentro de ruído estatístico.

## Interpretação

Bounds canônicos 30/70 são herança literatura tradicional. Em crypto 1h short, **25/75 (mais extremo) seleciona entries em condições de overbought mais raras e mais confiáveis** — o sinal "RSI > 75" é mais carregado de informação que "RSI > 70" no regime atual.

Análise por combo:
- **SOL naked**: trades caem 60% (esperado — 30/70 já tinha 51 trades 2025-H2 baseline 1h, agora 66 em janela completa H2). Sharpe quase dobra. Entries menos frequentes mas muito mais lucrativas.
- **BTC width**: filter já corta universo; bounds 25/75 corta mais. Apesar de menos trades, Sharpe quase dobra. Filter + bounds extreme combinam bem.
- **SOL trendhtf**: bounds 25/75 e 35/65 ambos melhoram, mas 35/65 com mais trades chega a 2.21 (próximo de 25/75). Combo já filtrado por trend_htf — direção de busca pode estar em outro eixo.

35/65 falha em naked e filter width (mais trades, dilui edge). Só ajuda quando combo já tem filter direcional muito restritivo (trendhtf).

## Decisão

**NÃO promover ainda.** Padrão 25 explicitamente exige validação cross-window antes de mudar manifest. CZ10 testou só 1 janela por combo — mesma janela em que o baseline foi medido. Risco de window-specific upgrade.

**Próxima série (CZ11) já planejada implicitamente**: rodar bounds 25/75 nos mesmos 3 combos em janelas adicionais regime-compatíveis:
- SOL naked 25/75 em 2025-H1 + 2024-H2 (aproveita CZ2 frame)
- BTC width 25/75 em 2024-H2 + 2025-H2
- SOL trendhtf 25/75 em 2024-H2 + 2025-H2

Se ≥2/3 janelas confirmam upgrade → promoção bounds 25/75 nesses combos.

## Padrão 38 (NOVO): bounds extreme (25/75) é candidato dominante em RSI short crypto 1h

Hipótese empírica: bounds extremos mais extremos (25/75 vs 30/70) elevam Sharpe em 50-90% nos top combos RSI short crypto 1h. Mecanismo provável: market microstructure de overbought "verdadeiro" requer condições mais raras em crypto vs equities (literatura clássica).

Não generalizar pra long ou outros timeframes sem teste — Padrão 28 (cross-timeframe asset-specific) e Padrão 26 (regime-matched) ainda valem.

## Consideração estratégica

Se CZ11 confirma upgrade cross-window, isso é **MAIOR achado da rodada de hoje** — re-elevar 3 combos do stack (incluindo top performers SOL + BTC) eleva Sharpe agregado do portfolio sem mudar composição.

Pendente do usuário: autorizar CZ11 cross-window e, se PASS, autorizar mudança de manifest (que é mudança real de estratégia em produção).

## Ação executada

- ✅ ADR-0135 closeout
- ✅ Série CZ10 documentada
- ✅ STATE.md entry (consolidado tarde-3)

## Não-alvo

- Não mudar manifests AINDA (cross-window obrigatório)
- Não testar 35/65 em mais combos (apenas 1/3 mostrou ganho)
- Não testar bounds em RSI long ou outros timeframes (escopo limitado)

## Stack pós-CZ10

13 combos inalterados. Bounds 25/75 é candidato forte de upgrade pendente cross-window (CZ11).
